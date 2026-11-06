Completion-correct paired versus serial transpose: original16-cell screen

Control: frozen b139 plus original serial helper with seven completion waits(R2, b357ecfd). Candidate: frozen b139 plus shared paired phases with completion waits(R1,232e3a6a). Positive percentages mean pairing is faster. Both arms passed39 exact cases and76 matched resource checks. This isolates pairing/order from the required completion fix; the earlier R1-vs-b139 experiment remains separate.

Primary aggregate: -0.222%; decode +0.132%; prefill -0.575%. Eleven cells improve and five regress. All6,400 strict CUPTI samples,32 source-bound runtime-guard receipts and128 loaded functions(LOCAL0) were verified. No rows were dropped or replaced.

Each cell uses100*(sqrt(C1*C2)/sqrt(A1*A2)-1); aggregate ratios use a geometric mean. Native winners, routes, publicAPI, input-quantizer contract, cold-L2 graphs,10warmups/100samples and stock clocks are unchanged. Arithmetic phase-pair estimates are diagnostic columns in cells.csv.

Pairing affects gated per-token and non-gated/ReLU2 callers, so ordinary N3U is affected too. The expanded39-case codegen comparison has62/76 identical PTX files(all37FC2);14FC1 files differ with unchanged resources. The sampled narrow/wide paired bodies halve store-completion fences.

|Model/topology|Mode|Tokens|C1 us|A1 us|A2 us|C2 us|Pairing speedup|C spread|A spread|
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
|kimi-k3 EP|PER-TOKEN|8|83.2330|83.1690|83.2010|83.2330|+0.058%|0.000%|0.038%|
|kimi-k3 EP|PER-TOKEN|16384|1025.6280|1056.9400|1057.6450|1055.5170|-1.592%|2.914%|0.067%|
|nemo3-ultra EP|W4A4|8|47.5040|47.6485|47.4570|47.9525|+0.368%|0.944%|0.404%|
|nemo3-ultra EP|W4A4|16384|594.1985|591.3990|590.2620|593.9270|+0.547%|0.046%|0.193%|
|v3 EP|MXFP8|8|88.6090|88.4490|88.4655|88.4810|+0.099%|0.145%|0.019%|
|v3 EP|MXFP8|16384|703.9120|734.1205|752.8090|750.1850|-2.250%|6.574%|2.546%|
|v41-flash EP|MXFP4x8|8|49.9685|49.9200|49.8245|49.9210|+0.145%|0.095%|0.192%|
|v41-flash EP|MXFP4x8|16384|822.9695|832.6815|830.5220|801.8810|-2.314%|2.630%|0.260%|
|kimi-k3 TP|MXFP4x8|8|79.8885|79.7770|79.8885|79.8410|+0.040%|0.059%|0.140%|
|kimi-k3 TP|MXFP4x8|16384|1622.4290|1622.3340|1624.3980|1633.5335|+0.284%|0.684%|0.127%|
|nemo3-ultra TP|PER-TOKEN|8|63.8240|63.8090|63.7130|64.0320|+0.262%|0.326%|0.151%|
|nemo3-ultra TP|PER-TOKEN|16384|1812.2230|1803.7910|1805.4870|1812.6230|+0.431%|0.022%|0.094%|
|v3 TP|MXFP8|8|71.0880|71.1360|71.1360|71.1530|-0.022%|0.091%|0.000%|
|v3 TP|MXFP8|16384|1342.2990|1339.5630|1340.7955|1347.6430|+0.357%|0.398%|0.092%|
|v41-flash TP|W4A4|8|52.6405|52.5765|52.5605|52.6090|+0.107%|0.060%|0.030%|
|v41-flash TP|W4A4|16384|1043.5765|1042.9200|1043.7685|1042.9525|-0.008%|0.060%|0.081%|

N3U EP W4A4 and N3U TP per-token prefills improve0.547% and0.431% with tight phase repeats. K3 EP per-token prefill appears1.591% slower but its control varies2.914%; its within-phase quartiles also drift, so this is not a stable regression claim. V3 EP MXFP8 and V41F EP MXFP4x8 are single-fragment source controls with similarly noisy prefill losses. All remain in the reported aggregate.

No56-cell expansion or retention decision follows from this original screen alone. A separately authorized three-cell repeat is stored under paired-vs-serial-tmem-repeat; it does not replace or merge into these original rows.

The active local reviews have been composed onto retained77391e28; these timings remain b139-based and make no claim about the unmeasured composition. Full source manifests, raw CUPTI timelines, per-phase components, exposed critical-path extensions and clock quartiles are preserved under evidence/results.
