# Four-element workers for unweighted combine

Candidate `e26fb67beca1896e3ee7bfbcae69ab9efca5c3fe` builds on PR9 head
`f4c521f5db98db16ae75e1a54381c57aab6a220a`. The same-mode control is J1
`2a4986d1ab0f00f2535e2ee8f069b9ce82bad0c0`; its kernel, frontend, reference,
and benchmark bytes are unchanged at f4c.

Only `apply_topk_in_fc1=True` uses four hidden elements per reducer worker
instead of eight. This doubles logical workers and spreads smaller combine
outputs over more of the existing CTAs, with 64-bit contiguous memory copies
and two packed FP32 pairs. The first-term assignment and ordered slot additions
are unchanged. False keeps eight-element/128-bit workers.

The implementation adds no public option, tactic, barrier, warp role, grid
change, or alignment requirement. The existing one-CTA-per-SM execution remains.
The destination alignment guarantee weakens from 16 to 8 bytes for the narrower
copy. Supported hidden dimensions are multiples of 32. Source coverage checks
exercise 144 cases and 1,823,796 worker tiles, including partial and multistripe
tails. Source review is not compilation or GPU correctness evidence.

Risk: more worker-index operations and smaller memory vectors could worsen
large-workload efficiency. Run the complete 13-shape AUTO4/O3 sweep using the
unchanged cold-L2 CUPTI graph method. Compare K1 directly to J1 on the same
node/boot and require all 104 same-contract outputs to match bit-for-bit.
Decode4–512 is primary; 1/2 remain report-only and each prefill size is checked.
Do not compare cross-mode output bits or infer performance from source counts.

Keep this isolated branch unpromoted until results justify it. Any useful gain
still needs the numerical/sanitizer qualification for the FC1-weighted mode.
