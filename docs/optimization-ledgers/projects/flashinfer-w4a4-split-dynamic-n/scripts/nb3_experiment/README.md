# Three channel tiles sharing B (13ca)

Rejected isolated FC1 prototype. Logical M768/N128 issues three physical M256
MMAs perK stage, sharing B/SFB. It uses three operand stages; accumulator384,
SFA48 and SFB16 columns fit512 TMEM columns. All A/SF/MMA channel loops are
compile-time unrolled; no problemH/I/T branch. Production FC2 stays unchanged.

Native NVFP4 T16384, same13ca routing/weight preparation,10/100 cold-L2 graph
CUPTI. Complete output bytes match. FC1 production/prototype/production:
284.545 /288.785 /283.473us. Full chain563.585 /565.601 /561.393us. The reduced
activation traffic does not offset the larger tile/shallower ring. No retention.

Initial r1 failed host FC1 validation for the new logicalM768; no candidate
GPU timing. r2 explicitly patches the isolated validation alias. Raw results
and failure logs are preserved. Do not apply this prototype to FC2: its MMA
accumulator loop is specialized to non-overlapping FC1 storage.
