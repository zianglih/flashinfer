# Selected-C1 Nsight Systems result

The selected `7dc96269` forward contains **one MegaMoE CUDA graph kernel per replay**, including input staging and ordered Top-K reduction. All 16 reports (8 ranks ×128/8192 tokens) show exactly five executions of that single graph node: 80 MegaMoE executions total, with no separate staging or TopkReduce launch. Cache-eviction fills and rank synchronization appear outside the forward graph.

| Tokens | Final-C1 selected tactic | Threads/CTA | Registers at launch | CUBIN stack/local bytes | SASS local loads/stores | Dynamic shared bytes |
|---:|---|---:|---:|---:|---:|---:|
|128|N64, epilogue return, stages 2|640|96|0 /0|0|200064|
|8192|N128, dispatch return, stages 2|640|96|0 /0|0|230784|

Both run the fused int32/vector ABI. The actual PTX retains control 80, dispatch 64, epilogue 144 register redistribution; both decode WGs retain the initial 96 budget. CUBIN reports 1024 bytes of static shared storage separately from the launch's dynamic allocation. These observations agree across all 8 ranks per shape.

For 8192, the outgoing shared-to-global bulk copy is followed by `cp.async.bulk.commit_group` and **full `cp.async.bulk.wait_group 0`**, without `.read`. The other full wait belongs to the dispatch-pull leg. No weakened return completion was introduced.

This is launch-boundary and static-code evidence, **not an internal-phase timing breakdown**. The trace cannot attribute critical-tail time to decoding, dispatch drain, barriers, or the integrated reducer. Five profiled replays are not used as benchmark medians. Graph DOT is unavailable; exported Nsight graph-node activities provide the launch evidence.

Source: `7dc9626909834bc70209e09784e9dfdebadceff2`, source manifest `eb0c8bbdadeab2fb511aadf2ee182231f9e052536793ff746d65baa3fb542742`; canonical `948e9a1` changes the README ledger and an autotune docstring, with no executable changes. Nsight Systems 2026.2.1, 8× B300 on hu-pdx-99. The immutable 579-member bundle is `collected-c1-selected/evidence.tar.gz`, SHA256 `5be3feff39c76b48086cc15f79558336ca4482d09d0e25e02905f4551a39ae9d`; all raw reports, SQLite exports, selected PTX/CUBIN/SASS and receipts are in its `evidence/` directory. Independent details: `selected-nsys-independent-audit.json`.
