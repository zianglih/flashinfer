| Backend | Stage | DRAM read bytes | DRAM write bytes | DRAM throughput % | Duration ns | SM throughput % | Tensor-pipe active % | Matches Nsight launch |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| CuteDSL W4A16 | FC1 + SwiGLU | 366118400 | 3186944 | 66.32 | 72640 | 51.72 | 48.4 | False |
| CuteDSL W4A16 | FC2 | 179254784 | 3090432 | 38.08 | 62432 | 49.57 | 27.42 | False |
| TRTLLM BF16 | FC1 + SwiGLU | 1233753344 | 3744000 | 91.43 | 176448 | 25.41 | 2.42 | False |
| TRTLLM BF16 | FC2 | 616780544 | 3596288 | 87.31 | 92640 | 24.19 | 2.3 | False |
