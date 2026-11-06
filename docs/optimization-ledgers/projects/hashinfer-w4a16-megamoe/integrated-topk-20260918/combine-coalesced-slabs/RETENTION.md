# Retention decision

Do not promote `329c690c682881be1273b1d22875a918d8504bae` over retained3de.
The complete hu15 full13 sweep passes104 finite BF16-bit output comparisons
and the existing source/fixture/environment/sample checks against A2; the
original sealed archive is `de285ec64cfa50bfb686e409f5a7f5a747c1e8e0d26eb38acdef482de272c203`.
Independent complete-file audit passed: all 59 original member hashes, all
104 exact outputs and 1,300 raw samples per arm, source/environment/closure,
and both primary A2 and historical A1 comparisons were verified. The audit is
`decode13-benchmark/independent-file-timing-audit.json` (SHA256 `c2d2853b63f3821530d0669e658812b1facab6dbc524c17dd57020ff22afa287`).
Original gzip bytes were not locally verified; the complete member bytes
were reconstructed from the sealed compact bundle and eight exact cached A1
files. Serial arms do not cancel drift; no sample trimming or rerun-based best
selection is used.

Decode4–512 geometric speedup is0.9955921x (3/8 wins), about0.443% slower.
Prefill4096/8192/16384 speedups are0.999554/0.965531/0.996969x.
The8K median slowdown is3.57%, with MAD16.24→30.53us;16K MAD is63.63→64.06us.
Only excluded1token changes its selected tactic. The new two-slab bulk
body begins only after the original first stripe, W = 512 * SM workers.
For canonical decode through T512, ceil(T/8) * (7168/8) is at most57,344,
so every decode output uses the original first stripe when SM >=112.
No direct SM-count field was present in the collected setup/timing metadata.
Existing same-hu15 generated PTX nevertheless embeds worker stride75,776,
which corresponds to148 SMs by the retained W=512*SM source formula; this
is a source-traced compile-time inference, not a new device query. Decode
variation therefore must not be attributed to execution of the new bulk
body. Changes in static code generation or allocation remain possible but
unproven. Nonpromotion rests on no demonstrated prefill benefit, including
the negative/noisy8K row.
No register-pressure or generated-instruction causal claim has been made.
Preserve the source for generated-code inspection or a separately measured
combination with shorter combine-score lifetimes; do not add a register
redistribution solely from the source-level accumulator size.

| Tokens | Retained A2 us | Coalesced I1 us | A2/I1 |
| ---: | ---: | ---: | ---: |
| 1 | 67.2640 | 67.7120 | 0.9934x |
| 2 | 86.4325 | 85.3760 | 1.0124x |
| 4 | 97.6480 | 96.9920 | 1.0068x |
| 8 | 121.1045 | 119.7935 | 1.0109x |
| 16 | 133.9045 | 135.9690 | 0.9848x |
| 32 | 160.9280 | 162.5600 | 0.9900x |
| 64 | 181.5205 | 183.8570 | 0.9873x |
| 128 | 188.7045 | 189.9210 | 0.9936x |
| 256 | 191.9045 | 191.7605 | 1.0008x |
| 512 | 195.7290 | 197.5205 | 0.9909x |
| 4096 | 464.6090 | 464.8165 | 0.9996x |
| 8192 | 777.6180 | 805.3790 | 0.9655x |
| 16384 | 1489.1595 | 1493.6865 | 0.9970x |
