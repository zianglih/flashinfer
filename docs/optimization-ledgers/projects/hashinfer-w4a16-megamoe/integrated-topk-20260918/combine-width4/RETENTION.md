# Width4 O1 retention: do not promote

Independent terminal file audit PASS (`0d4c43e8f2effde5292d3a7487327cd591c14221f58f3ed8f43b38d09fdae444`). All59 sealed original member files are locally verified by SHA256, including eight exact cached serialized outputs;104 outputs are finite/repeat-equal and bit-exact against both A3 and historical A1. All13 rows retain100 raw samples. Original gzip SHA062b3402 is seal-bound but **not locally verified**; no reconstructed-gzip claim.

Decode4–512 A3/O1 geometric speedup 1.002623997x, 5/8 faster; historical A1/O1 0.993638560x. All13 selected tactics match A3 on all8 ranks. Serial arms do not isolate temporal drift or generated-code causes.

| Tokens | A3 µs | O1 µs | A3/O1 | A1/O1 | A3 MAD µs | O1 MAD µs |
|---:|---:|---:|---:|---:|---:|---:|
|1|68.0640|75.8880|0.896901|0.878347|0.8480|0.8795|
|2|84.8330|85.5370|0.991770|0.930223|2.2080|0.8955|
|4|97.6650|96.4005|1.013117|1.007464|0.7365|0.8160|
|8|121.6165|122.4800|0.992950|0.957426|0.8955|1.0075|
|16|135.9210|134.8005|1.008312|0.998817|0.9280|0.7525|
|32|162.1290|161.0410|1.006756|0.998106|0.7520|0.8000|
|64|184.0335|184.3840|0.998099|0.991412|0.7995|0.7835|
|128|189.2325|188.0170|1.006465|1.000681|0.8485|0.8790|
|256|190.9920|190.8490|1.000749|0.997993|0.7520|0.8475|
|512|195.8410|196.8805|0.994720|0.998052|1.2160|0.7520|
|4096|460.7050|465.1375|0.990471|0.999897|3.5205|4.1600|
|8192|798.4855|766.6590|1.041513|0.991212|30.0335|10.4650|
|16384|1499.5880|1495.7485|1.002567|1.001351|80.8170|71.5390|

## Dispersion and decision

| Tokens | A3 chronological quarter medians µs | O1 chronological quarter medians µs |
|---:|---|---|
|1|68.897/67.360/68.032/68.161|76.032/75.872/75.488/76.192|
|2|162.785/109.025/83.456/84.384|86.112/85.216/85.248/85.728|
|4|97.696/97.569/97.856/97.665|96.353/96.544/95.712/96.257|
|8|122.273/121.312/121.441/121.697|123.041/122.304/122.113/122.785|
|16|136.481/135.425/135.680/136.320|135.136/134.817/134.784/134.113|
|32|162.049/162.241/162.050/162.145|161.121/160.832/161.280/161.025|
|64|184.353/183.521/184.609/183.713|184.641/184.001/183.713/184.449|
|128|189.857/189.153/188.577/189.249|188.193/187.938/187.777/188.161|
|256|191.361/191.105/190.721/190.913|191.424/190.593/189.793/190.976|
|512|196.737/195.457/195.329/195.936|197.153/196.481/197.249/197.089|
|4096|460.321/462.145/460.769/459.941|459.778/466.850/467.010/465.730|
|8192|764.003/762.850/810.499/826.757|762.755/761.122/788.354/821.251|
|16384|1357.764/1483.333/1558.404/1587.460|1359.625/1480.549/1565.797/1559.557|

The0.26% aggregate improvement against A3 is small and reverses against A1; A1/A2/A3 and prior L1/L2/N1/N2 already show sensitivity to timing epoch. T4 improves1.29% in latency versus A3, but T8/64/512 regress and T256 is essentially flat. T1, excluded from the retention aggregate but still a required visible workload, regresses11.50% in latency with separated quarters despite the same tactic.

Prefill4096 regresses0.96% in latency. The8K median gain against A3 coexists with O1 quarters762.755/761.122/788.354/821.251µs and is negative against A1;16K has a large chronological ramp and71.539µs MAD. Neither supplies clean evidence of a general benefit.

Keep weighted width8 d01/retained3de device behavior. This trial confirms exact numerics but does not justify width4 promotion or further GPU qualification. No codegen/sector/register-pressure explanation is inferred from this timing table. Benchmark-first policy preserved; no sanitizer or new native pretest.
