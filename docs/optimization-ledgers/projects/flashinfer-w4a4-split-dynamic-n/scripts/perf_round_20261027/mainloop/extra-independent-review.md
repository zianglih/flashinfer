# Multicast short-K and channel-tail gate

The frozen `c9854f44` candidate is admitted to the model performance screen. The extra review independently verifies all 314 collected artifact hashes and the exact `1d6459e6` probe, 64 paired replay outputs, 32 core pairs, and four encoding-identical PrepareRouted pairs. Together with the base review this is 128 exact replay comparisons, 64 core pairs and 14 PrepareRouted pairs.

All four formats (NVFP4, per-token NVFP4, MXFP8, MXFP4x8) cover static and CLC scheduling, both FCs and both PDL settings at M256/N128. Each FC1 has reduction size 384 and a partial final K stage. Each FC2 has output width 384, leaving the second CTA inactive on the final channel tile. Changing, empty and reactivated routes exercise dynamically shortened token tiles. The captured core metadata confirms these cases actually reach the wide two-CTA SFB path.

All 32 changed cores emit CTA0-only SFB multicast with mask 3. Register, static/dynamic shared-memory, stack/local-memory, stage, TMEM and UMMA-commit metadata remains equal. There are no local-memory spill instructions. Every expected transaction byte immediate and every wait, barrier-arrival, fence, UMMA-commit and PDL site count agrees between sources. Unlike the MXFP8 FC1 base case, this extra matrix adds no initialization-fence sites.

The extra cores add 672 static instructions including NOP padding, or 546 excluding it. Owner/mask/address work is present in the unrolled issue paths; uniform-register allocation and transfer choices also change. This gate establishes correctness and bounded resource behavior, not a total instruction reduction or performance improvement. The public-path fixed-tactic model screen is the retention evidence.

The reproducible, read-only reviewer is `review_extra_codegen.py`; per-core counts, ownership registers and source hashes are in `extra-independent-review.json`. No GPU reruns or source changes were performed by this review.
