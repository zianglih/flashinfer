# Active optimization handoff — 2026-10-29

Continue optimizing fork PR8 until user stops. Swap-AB and W4A16 no standalone FC1 permutation; V3/V41F/K3/N3U, EP/TP, supported dtypes. Do not modify upstream PR7290. No sanitizer during iteration. Keep active source changes unstaged; retire rejected/superseded copies while retaining helper evidence.

## Retained and published

Canonical `flashinfer-fc1-gather-review` is clean and pushed at `f63e948564582a487f95900c71ef581b90c3f177`. This adds useful-scale-block-based CTA width for shared per-token quantization (+9/-5) to475cae6b W4 five-WG Gather4. Latest publication `per-token-width-475/publication/receipt.json`: body SHA2e4209aaaee6e6572e58de7a38c8beaa4906b0fafebc4478753dff4908c1ad83, assets7a6356e2743e336e2917f913c0c12bab6268d67c.468raw/396displaycells;104freshperToken+364source-equivalent475cells. Vs saved d35 EP+0.63%,TP+5.79%,TPprefill+14.67%; historical GPU-instance caveat explicit. TRTLLM impact audited: initial H policies unchanged; intermediate quantizer nativeC++, not modified Python code. Old TRT controls remain reusable.

Quantizer retention:80existingexact tests,44directboundaries+176changing-live-count graphreplays+2routedholecases;24cellCAAC allfourmodels EP/TP, TPprefill+7.09%GM,8TPprefillcells+2.90..10.95%. Full104AA20,800CUPTI samples,514source-file matchf63. K3EP16KperToken3.82%repeatclockcaveat retained. Full evidence under`per-token-width-475/`; source review copy retired after full equivalence proof.

W4 last/fifth gatherWG,640threads quotas144/80/96/96/64; FC2 originalfourWGs unchanged. Swapcontrol120/epi256/gather128. No new tactics.

## Current agents / GPU ownership

- root/GPU0: `per-token-register-width/` diagnostic with existing override, no source edit yet. Test large-M32thread width grown only by existing8block register budget; small-Mpolicy unchanged.12CAACmicrocases/exactoutputs/CUPTI. If retained it changes initialwidequantizer and TRT baseline needs appropriate reconsideration.
- full_bench_audit/GPU5: active `flashinfer-fc1-gather-sf-ownership-review`, base475. Reuse SFdecoded routeIDs forpayload. Firstprototype23exactpassed but N256oneCTA8Bspills and much largerSASS. Deferred64bitoffset repair didnotfix. Linear-bound/unsigned mapping repair23casegate running. NeedzeroLOCAL+cleanercodegen beforetiming. GPU7free.
- w4a16_table_audit/GPU6: terminalpipeline drain, fixedphysicalbarrier slots with phase `p XOR(slot<index)`; preserveallwaits andstagecapacity. Readonlyproof/codegengate; verifytailwaitreordercannotdeadlock.
- external_gap_audit: read-only audit of compiletime CTA/cluster relaypublication scope. NoGPUrun/sourceedituntilproposal. Finished publication and TRTbaselineproof.

## Rejected and retired this round

- Swapunsignedoffset:17exact,12cellCAAC4,800samples,−0.153%GM, no robustbenefit; feweruniformMOV.SPILLbut+18instructions/+2branches. `swap-gather-unsigned/` evidence; sourceretired.
- W4 election-scope:4moreinstructions/+1branch, zeroLOCAL; sourceequivalent butnotcleanercodegen, no perf campaign. `full-20261029/w4a16-elected-issue/`; sourceretired.
- Swaplivegroups, rowouterlivegroups, W4livegroups allregressprefill; donotrepeatwithoutnewmechanism. Predicatedrowpruning alreadyrejected too.
- Existinggraph-onlyautotuneexperiment sourcecopyretired, evidencepreserved. Actual-routefirst-calltuning rejectedbydummywarmupholdout; no routecachekey ornewtacticaxis.

## Runtime / caches

C3 `fi-gather-opt-1029`,namespaceziangli,8B300,`nvcr.io/nvidia/pytorch:26.05-py3`,CUDA13.2,CuTeDSL4.8.0. Managed `/usr/local/bin/h`,cwd`/Users/ziangli/rl/hai`; wrapper`optimization-20261028/swap-ab-hybrid-output/remote_box.py`. Old1028boxgone,/data persisted. Remoteparent`/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/fc1-gather-20261028`,active`optimization-next-20261029`.

Nativecache`compile`,DSL`compile/cute-dsl-4.8.0-cuda13.2-sm103`. New clones must link whole `flashinfer/data` to same stable target as `composed-w4-final/flashinfer-candidate`; reconstructing individual include symlinks triggers C++rebuild. Neverdeletecache/locks. Persistentcachewait investigatedwithread-onlypy-spy; notGPUdeadlock.

NCUhangsontrivialallocation;donotroutinelyretry. UseCUPTI/SASS/iKET/NSYS. Noactiveclocklocks. ReadonlyNVML2mstelemetryhelpers kept. PublicGHbatch switch+verifyzianglih, noauthsetup-git. Sourcecopyclonesuse `--no-local --no-hardlinks --depth1 file://` due historicalmissingobject. OlderPR7290reviewcopies outside thiseffortchain remainuntouchedpendingownershipaudit.
