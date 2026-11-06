# Role-local TMEM pointer screen

Candidate: b52 + kernel `06c882e4`, 3 insertions / 2 deletions; rejected after the bounded repeat. Allocation, waits, barriers, release/free ownership and all arithmetic stay unchanged.

Qualification: 16 initial compile-only signatures pass the original strict resource checks. Numerical coverage is 40 original exact passes plus a separate rerun of the final case. Its FC2 REG82→83 is explicitly qualified by identical22528 physical registers/CTA, unchanged215936B dynamicSMEM and oneCTA/SM occupancy; original failed strict guard remains preserved. Both inherited MX stress spills stay128B/16LDL/16STL, but uniform-spill instructions increase in those cases. No general register-pressure improvement is claimed.

The fresh complete22-cell screen uses frozen native tactics/routes, publicAPI, stockclocks, coldL2 CUDAgraphs and100 strictCUPTI samples per CAAC phase. There are20 affected swap cells plus2 source-identical W4A16 controls. All8800samples,176 loadeddriver guards,514source hashes and rawmedians passed audit; no newnativeLOCAL and no missingNVMLquartiles. Normalcache exposes no binaryimage for all176loads, so runtimebinaryidentity is not claimed. W4actual calls, sourceclosure and frozenchoices were verified.

|Affected group|Cells|Geometric change|
|---|---:|---:|
|all/all|20|-0.172%|
|all/decode|10|-0.045%|
|all/prefill|10|-0.299%|
|ep/all|10|-0.460%|
|tp/all|10|+0.116%|

11/20 affected rows are negative. N3U EP MXFP8 T16K is the original retention blocker:−6.523%, with control843.173/794.420us and candidate875.877/875.221us. Both FC1 and FC2 spans are slower. The largecontrolspread and latephase drift remain diagnostic uncertainties; candidate is slower than bothcontrols, so the loss is not dismissed. One predeclared freshsameGPU repeat of that row plus source-identical V3EP W4A16T8 is reported separately under `tmem-pointer-scope-repeat`. Originalaggregate remains unchanged.

No timing is reused from abandonedR0: normalcompiled artifacts.CUBIN wasNone and bothfirstcontrols failed before firstownedcallable return. R1 readsnormal-loaderIR optionally and explicitly recordsunobserved when absent; nocompilerflags were changed.

Fullrawtable: `evidence/table.md`; allFC spans: `components.md`; raw/sourceaudit: `raw-audit.json`; originaldrift: `n3u-mx8-drift-audit.json`.

Final decision: rejected. The separate repeat is −5.307% for N3U EP MXFP8 T16K with both candidate phases slower than both controls; unchanged W4 control +0.153%. See `../tmem-pointer-scope-repeat/RESULTS.md`. No original row or aggregate changed.
