"""Observe unchanged W4 default resolution and the exact compiled callable.

Only host metadata is read during the existing prewarm/capture calls. No GPU
work, arguments, compiler options, cache entries, or timing code is changed.
"""
import hashlib,inspect,json
from pathlib import Path

def install(tuner,active_measurement,to_json):
    from flashinfer.fused_moe.cute_dsl.blackwell import moe_w4a16 as host
    default=host.DEFAULT_W4A16_MOE_TACTIC
    assert default==(((256,128,256),(2,1),True),((256,128,256),(2,1),True))
    sources={Path(m.__file__).name:hashlib.sha256(Path(m.__file__).read_bytes()).hexdigest() for m in (host,tuner)}
    original_launch=tuner.launch_w4a16_moe
    original_get=host._get_compiled_kernel
    signature=inspect.signature(original_get)
    current=None
    def launch(**kw):
        nonlocal current
        assert current is None
        supplied=kw['tactic'];resolved=default if supplied is None else supplied
        current={'tokens':int(kw['x'].shape[0]),'supplied_moe_tactic':to_json(supplied),'resolved_moe_tactic':to_json(resolved)}
        try:return original_launch(**kw)
        finally:current=None
    def get(*args,**kwargs):
        assert current is not None
        bound=signature.bind(*args,**kwargs).arguments
        stage='fc1' if bound['gather_input'] else 'fc2'
        expected=current['resolved_moe_tactic'][0 if stage=='fc1' else 1]
        assert list(bound['mma_tiler_mnk'])==expected[0]
        assert list(bound['cluster_shape_mn'])==expected[1]
        assert bool(bound['raster_along_m'])==expected[2]
        compiled=original_get(*args,**kwargs)
        measurement=active_measurement()
        if measurement is not None:
            row=dict(current,stage=stage,shape_mnk=[int(bound[k]) for k in ('m','n','k')],mma_tiler_mnk=list(bound['mma_tiler_mnk']),cluster_shape_mn=list(bound['cluster_shape_mn']),raster_along_m=bool(bound['raster_along_m']),use_clc_scheduler=bool(bound['use_clc_scheduler']),enable_pdl=bool(bound['enable_pdl']),max_active_clusters=int(bound['max_active_clusters']),compiled_library=int(compiled.library))
            seen=measurement.setdefault('w4_resolved_configs',[])
            if row not in seen:seen.append(row)
            measurement['w4_resolution_source_sha256']=sources
            measurement['w4_default_tactic']=to_json(default)
        return compiled
    tuner.launch_w4a16_moe=launch
    host._get_compiled_kernel=get
