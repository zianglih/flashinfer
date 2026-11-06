# DSV Flash: AUTO12 M256-only comparison

Median of100 untrimmed CUPTI rank-MAX samples per point; one fresh EP8 process group per capture.
Independent native AUTO12 versus saved scheduler-OFF AUTO24; BEFORE reused. Selected tactics may differ. No fixed-tactic or cross-model comparison.
AUTO12 speedup versus AUTO24 = AUTO24 median / AUTO12 median; above1 favors AUTO12.
Report every point; exclude only1/2 from aggregates. Final catalog decision belongs to the owner.

| Tokens | BEFORE µs | BEFORE tactic | OFF AUTO24 µs | AUTO24 tactic | OFF AUTO12 µs | AUTO12 tactic | AUTO12 / BEFORE | AUTO12 / AUTO24 |
|---:|---:|---|---:|---|---:|---|---:|---:|
| 1* | 62.2090 | M256/N64/G512/epi | 66.8965 | M256/N32/G1024/epi | 67.8730 | M256/N64/G512/epi | 0.91655× | 0.98561× |
| 2* | 66.3685 | M256/N64/G1024/epi | 67.2010 | M128/N32/G1024/epi | 69.4250 | M256/N32/G512/epi | 0.95597× | 0.96797× |
| 4 | 71.7455 | M256/N64/G512/epi | 60.8805 | M128/N32/G512/epi | 72.9605 | M256/N32/G1024/epi | 0.98335× | 0.83443× |
| 8 | 86.4810 | M256/N64/G1024/epi | 88.0335 | M128/N32/G512/epi | 88.6410 | M256/N32/G512/epi | 0.97563× | 0.99315× |
| 16 | 102.3375 | M256/N64/G1024/epi | 103.2010 | M128/N32/G512/epi | 103.1850 | M256/N32/G512/epi | 0.99179× | 1.00016× |
| 32 | 122.5935 | M256/N64/G512/epi | 130.5450 | M128/N32/G1024/epi | 127.0410 | M256/N32/G512/epi | 0.96499× | 1.02758× |
| 64 | 172.0020 | M256/N64/G1024/epi | 167.4900 | M128/N32/G1024/epi | 168.0175 | M256/N32/G1024/epi | 1.02371× | 0.99686× |
| 128 | 210.7060 | M256/N64/G1024/epi | 204.2095 | M128/N32/G512/epi | 201.0425 | M256/N32/G512/epi | 1.04807× | 1.01575× |
| 256 | 214.7700 | M256/N64/G512/epi | 208.3690 | M128/N32/G1024/epi | 208.4980 | M256/N32/G512/epi | 1.03008× | 0.99938× |
| 512 | 217.0105 | M256/N64/G512/epi | 212.2415 | M128/N32/G1024/epi | 208.3545 | M256/N32/G1024/epi | 1.04154× | 1.01866× |
| 4096 | 332.7555 | M256/N128/G1024/dispatch | 333.7485 | M256/N128/G512/epi | 330.2280 | M256/N128/G512/epi | 1.00765× | 1.01066× |
| 8192 | 500.9490 | M256/N128/G1024/dispatch | 503.1105 | M256/N128/G512/dispatch | 503.8930 | M256/N128/G1024/dispatch | 0.99416× | 0.99845× |
| 16384 | 873.7860 | M256/N128/G1024/dispatch | 860.3615 | M256/N128/G1024/dispatch | 866.6790 | M256/N128/G1024/dispatch | 1.00820× | 0.99271× |

| Tokens | AUTO24 p25–p75 µs | AUTO24 tactic | AUTO12 p25–p75 µs | AUTO12 tactic | AUTO12 µs saved | AUTO12 latency reduction |
|---:|---|---|---|---|---:|---:|
| 1 | 66.0168–67.5768 | M256/N32/G1024/epi | 67.0088–68.9370 | M256/N64/G512/epi | -0.9765 | -1.460% |
| 2 | 66.3680–68.0727 | M128/N32/G1024/epi | 68.7687–70.1607 | M256/N32/G512/epi | -2.2240 | -3.309% |
| 4 | 60.0883–62.2163 | M128/N32/G512/epi | 72.0722–74.0890 | M256/N32/G1024/epi | -12.0800 | -19.842% |
| 8 | 87.1290–89.3850 | M128/N32/G512/epi | 87.9600–89.7450 | M256/N32/G512/epi | -0.6075 | -0.690% |
| 16 | 102.4570–104.7050 | M128/N32/G512/epi | 102.3610–104.1532 | M256/N32/G512/epi | 0.0160 | 0.016% |
| 32 | 129.6017–131.2810 | M128/N32/G1024/epi | 126.2730–128.0090 | M256/N32/G512/epi | 3.5040 | 2.684% |
| 64 | 166.7380–168.3620 | M128/N32/G1024/epi | 167.1940–168.7218 | M256/N32/G1024/epi | -0.5275 | -0.315% |
| 128 | 203.1540–205.5700 | M128/N32/G512/epi | 200.4180–201.8980 | M256/N32/G512/epi | 3.1670 | 1.551% |
| 256 | 207.3617–209.2730 | M128/N32/G1024/epi | 207.6667–209.3780 | M256/N32/G512/epi | -0.1290 | -0.062% |
| 512 | 211.3853–213.1533 | M128/N32/G1024/epi | 207.7150–208.8748 | M256/N32/G1024/epi | 3.8870 | 1.831% |
| 4096 | 332.6360–335.1567 | M256/N128/G512/epi | 328.7088–331.5800 | M256/N128/G512/epi | 3.5205 | 1.055% |
| 8192 | 500.0943–506.0947 | M256/N128/G512/dispatch | 501.3010–506.9170 | M256/N128/G1024/dispatch | -0.7825 | -0.156% |
| 16384 | 829.2012–874.0660 | M256/N128/G1024/dispatch | 831.0790–877.6480 | M256/N128/G1024/dispatch | -6.3175 | -0.734% |

- all11: AUTO12/BEFORE 1.00596×; AUTO24/BEFORE 1.01777×; AUTO12/AUTO24 0.98839×.
- decode4_through512: AUTO12/BEFORE 1.00695×; AUTO24/BEFORE 1.02346×; AUTO12/AUTO24 0.98386×.
- prefill: AUTO12/BEFORE 1.00332×; AUTO24/BEFORE 1.00274×; AUTO12/AUTO24 1.00058×.

All13×8 selected tactics, source/runtime/fixture controls and native raw-sample medians are validated. Adjacent JSON keeps every raw sample and receipt; no pooling or trimming. Tuning scoreboards remain a separate diagnostic.
