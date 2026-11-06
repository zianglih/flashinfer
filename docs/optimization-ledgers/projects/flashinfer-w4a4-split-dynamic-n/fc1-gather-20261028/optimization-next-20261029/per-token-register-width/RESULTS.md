# Register-budget width diagnostic — rejected

Using existing per-token thread override at f63, start throughput rows at32 threads and grow only for the existing8-block register budget. Small-M policy unchanged. This is a width-only diagnostic, no source candidate. Same-input exact payload/scales/row scales;12CAACcases,4,800strictCUPTI samples,10warmups,cold-L2graphs,B300GPU0.

|M|K|Control threads|Diagnostic threads|Control us|Diagnostic us|Speedup|C/A repeat spread|
|---:|---:|---:|---:|---:|---:|---:|---:|
|360448|640|64|32|395.290|384.674|+2.76%|0.02%/0.09%|
|98304|576|64|32|110.193|106.609|+3.36%|0.09%/0.03%|
|262144|384|32|32|184.137|184.105|+0.02%|0.10%/0.04%|
|131072|256|32|32|90.945|91.032|-0.10%|0.28%/0.09%|
|16384|1536|96|32|34.384|27.424|+25.38%|0.09%/0.23%|
|16384|2048|128|32|41.200|35.272|+16.81%|0.08%/0.68%|
|16384|2304|128|32|50.336|43.712|+15.15%|0.13%/0.44%|
|16384|3072|128|32|55.784|61.864|-9.83%|0.03%/0.44%|
|16384|3584|128|32|61.217|76.280|-19.75%|0.05%/0.10%|
|16384|5120|128|64|79.816|74.537|+7.08%|0.10%/0.11%|
|16384|7168|128|64|105.216|124.001|-15.15%|0.00%/0.08%|
|128|640|64|64|2.960|2.960|+0.00%|1.09%/1.09%|

The broad policy is rejected:K3072,K3584,K7168 regress9.83%,19.75%,15.15%. A separate diagnostic CUBIN capture confirms new local spills for those narrow-width choices (96/128/128-byte stack), while retained widths are zero-stack. This is not evidence for problem-specific width exceptions. The no-SMEM one-warp reduction cleanup is isolated separately in `../per-token-warp-reduce/` with retained width policy.

Quantizer source SHA2bb9ed15d2ba33520c6c8b015e43fe2d9d8a01fa08541dc7384c9163842ad0dc. Initial evidence archiveSHA1fa9799f10b6bf6fed407a16ec7bf78bf86e83e3d031f1256eea72bff90453cf; codegen supplement pending fetch. No repository source changes.
