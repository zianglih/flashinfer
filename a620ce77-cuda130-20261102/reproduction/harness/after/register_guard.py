"""Check the loaded CUDA kernel's register reservation before its first launch."""
import hashlib,json,os
from pathlib import Path
import subprocess,time


def install():
    import cutlass.cute as cute
    import cuda.bindings.driver as cuda
    import flashinfer

    repo=Path(os.environ['REG_GUARD_REPO']).resolve()
    source_file=Path(os.environ['REG_GUARD_SOURCE'])
    source=json.loads(source_file.read_text())
    assert Path(flashinfer.__file__).resolve().is_relative_to(repo)
    policy={k:int(os.environ['REG_GUARD_'+k.upper()])for k in ('control','gather','epilogue')}
    expected_policy = source['register_policy']
    assert policy == expected_policy
    sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

    def verify():
        assert source['head']==os.environ['FI_FROZEN_HEAD']
        for name,h in source['source_sha256'].items():assert sha(repo/name)==h,name
        assert source['source_sha256']['flashinfer/fused_moe/cute_dsl/blackwell/moe_swap_ab_kernel.py']==os.environ['REG_GUARD_KERNEL_SHA']

    def checked(result):
        assert result[0]==cuda.CUresult.CUDA_SUCCESS,result
        return result[1] if len(result)==2 else result[1:]

    verify()
    out=Path(os.environ['REG_GUARD_OUTPUT'])/str(os.getpid());out.mkdir(parents=True,exist_ok=False)
    original=cute.compile
    receipt=dict(started=time.time(),source_file=str(source_file),source_sha256=sha(source_file),kernel_sha256=os.environ['REG_GUARD_KERNEL_SHA'],policy=policy,compilations=[],compiler_options_changed=False,boundary='Unmodified cute.compile and normal caches. compiled.library loads the exact executable without launch; CUDA driver queries initial registers, maximum threads, and local bytes before returning the callable. Static source role/policy proof and prior cubin validation supply donation targets; this query does not inspect SASS.')
    def save():(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    save()

    def guarded(*args,**kwargs):
        kernel=getattr(args[0],'__self__',None)
        owned=type(kernel).__name__=='Sm100BlockScaledGroupedGemmKernel'
        compiled=original(*args,**kwargs)
        if not owned:return compiled
        device=checked(cuda.cuCtxGetDevice())
        library=cuda.CUlibrary(int(compiled.library))
        count=int(checked(cuda.cuLibraryGetKernelCount(library)))
        assert count==1,('Expected one owned executable kernel',count)
        handles=checked(cuda.cuLibraryEnumerateKernels(count,library))
        assert len(handles)==1
        handle=handles[0]
        name=checked(cuda.cuKernelGetName(handle))
        if isinstance(name,bytes):name=name.decode()
        values={key:int(checked(cuda.cuKernelGetAttribute(getattr(cuda.CUfunction_attribute,'CU_FUNC_ATTRIBUTE_'+attr),handle,device)))for key,attr in [('initial_regs','NUM_REGS'),('max_threads','MAX_THREADS_PER_BLOCK'),('local_bytes','LOCAL_SIZE_BYTES'),('static_shared_bytes','SHARED_SIZE_BYTES'),('binary_version','BINARY_VERSION')]}
        r0=values['initial_regs'];threads=int(kernel.threads_per_cta)
        if kernel.gather_input:
            checks=dict(threads=threads==384,max_threads=threads<=values['max_threads'],control_donor=policy['control']<=r0,gather_donor=policy['gather']<=r0,epilogue_receiver=r0<=policy['epilogue'],pool=128*sum(policy.values())<=threads*r0)
        else:
            checks=dict(threads=threads==256,max_threads=threads<=values['max_threads'])
        checks['no_native_local'] = values['local_bytes'] == 0
        row=dict(index=len(receipt['compilations']),gather_input=bool(kernel.gather_input),kernel_name=name,library_handle=int(library),kernel_handle=int(handle),device=int(device),launch_threads=threads,checks=checks,passed=all(checks.values()),analysis=values,initial_regs=r0,required_pool=128*sum(policy.values()) if kernel.gather_input else None,available_initial_pool=threads*r0,compile_options=kwargs.get('options',''),route_tile=kernel.route_tile,cta_group_size=kernel.cta_group_size,tile_k=kernel.tile_k,activation_dtype=str(kernel.activation_dtype),weight_dtype=str(kernel.weight_dtype))
        receipt['compilations'].append(row);save();assert row['passed'],row
        return compiled

    cute.compile=guarded
    def finish(exitstatus):
        cute.compile=original;verify()
        receipt.update(finished=time.time(),exitstatus=int(exitstatus),all_guarded=bool(receipt['compilations']) and all(c['passed']for c in receipt['compilations']))
        save()
    return finish
