# W4A16-only retained-head refresh

Completed at `640877340375fee0169f659a329d08b660c33eca` (kernel `cf503fe43234deac7f11aa855f26a01afffb65189ccfcefd955988ec5ce1854a`). Eight B300 GPUs on `fi-moe-sanitize-1028`, image `nvcr.io/nvidia/pytorch:26.05-py3`; existing CUDA13.2/CuTe4.8 runtime and persistent native caches reused.

All eight jobs completed A1/A2: **104 cells,208 pass medians,20,800 strict CUPTI samples**. The public benchmark uses saved83df winners/routes,10warmups,100samples,cold-L2 CUDA graphs,swap-AB and unfused finalize. NV input quantization remains opt-in in the command; W4A16's BF16 input is not quantized. There is no tuning or external-control rerun.

The independent assembler verified source/Git blobs, helpers/runtime, GPU UUID/assignments, commands/environment, cache manifests,winner/routing identities,native CSV output,and every raw sample median. The full EP/TP tables retain all832non-W4rows and every control field; only the W4 column and104native W4A16 A2 rows changed. All13tokens were measured;1/2are omitted from the44row plots. Both red/green plots passed visual inspection and explicitly label new-head W4 versus other formats retained at83df.

`assembled/replacement-data.json` binds the two table/native-output/provenance sets. `final-receipt.json` also binds both PNG/SVG images. All source-bound raw receipts,samples and stdout are in `evidence/`; archive SHA `88fbd2914db8a5befe33207b3c529abb59f4f3c326f4dc664e9fb961fcf46df9` (799files verified).

For local review, `assembled/w4-comparison.json` separates historical83df comparison from the controlled32-cell retention experiment. Excluding1/2,the historical aggregate is+0.138% (EP−0.392%,TP+0.671%); EP prefill is−1.149%,TP prefill+1.404%. Three historical latency increases over3% remain visible: K3EP4096,K3EP8192,N3UEP8192. Their raw old/new pass medians are retained; these historical rows do not isolate source effects and are not labelled noise or replaced with diagnostic results. The matched combined32-cell screen remains separately reported at+0.400% overall and+1.273% on12partial-K cells.

Sanitizers were explicitly skipped for this iteration at the user's request. The retained W4 source has its existing exact/API/codegen qualification; no new sanitizer claim is made. This agent performed no PR or asset publication.
