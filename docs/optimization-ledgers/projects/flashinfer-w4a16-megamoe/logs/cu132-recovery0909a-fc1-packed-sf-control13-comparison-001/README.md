# Packed-SF complete CONTROL100 screen

Complete fixed CONTROL100 screening on hu-pdx-115. Candidate auto is unrun. Packed-SF changes only shared scale-factor bookkeeping over neutral f377. Retained38870 remains the promotion reference alongside neutral e359 and f377. Shared split source changes too. Unbracketed rows are preserved without minima or drift adjustment; no promotion from this arithmetic report.

| Tokens | Retained split ms | Retained Mega ms | e359 split ms | e359 Mega ms | f377 split ms | f377 Mega ms | Packed-SF split ms | Packed-SF Mega ms | vs retained | vs e359 | vs f377 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 0.078321 | 0.093409 | 0.091025 | 0.097713 | 0.084880 | 0.088193 | 0.091553 | 0.094113 | +0.754% | -3.684% | +6.713% |
| 2 | 0.118209 | 0.117889 | 0.114929 | 0.130209 | 0.115393 | 0.129825 | 0.105281 | 0.118113 | +0.190% | -9.290% | -9.021% |
| 4 | 0.151617 | 0.138209 | 0.144929 | 0.133649 | 0.150738 | 0.140321 | 0.151201 | 0.144977 | +4.897% | +8.476% | +3.318% |
| 8 | 0.177538 | 0.156386 | 0.171073 | 0.158305 | 0.169809 | 0.166450 | 0.167249 | 0.167681 | +7.223% | +5.923% | +0.740% |
| 16 | 0.191154 | 0.198770 | 0.189282 | 0.187634 | 0.194898 | 0.185634 | 0.194259 | 0.173314 | -12.807% | -7.632% | -6.637% |
| 32 | 0.219602 | 0.222435 | 0.219794 | 0.213634 | 0.208770 | 0.219170 | 0.204273 | 0.205666 | -7.539% | -3.730% | -6.161% |
| 64 | 0.228482 | 0.243602 | 0.234178 | 0.243410 | 0.226834 | 0.235587 | 0.251603 | 0.245090 | +0.611% | +0.690% | +4.034% |
| 128 | 0.257842 | 0.250066 | 0.247331 | 0.249938 | 0.243107 | 0.250658 | 0.229747 | 0.258387 | +3.328% | +3.380% | +3.083% |
| 256 | 0.261491 | 0.257570 | 0.260177 | 0.254786 | 0.256115 | 0.260562 | 0.245362 | 0.257618 | +0.019% | +1.112% | -1.130% |
| 512 | 0.256355 | 0.252083 | 0.251266 | 0.258323 | 0.255810 | 0.264466 | 0.250435 | 0.266514 | +5.725% | +3.171% | +0.774% |
| 1024 | 0.273970 | 0.277282 | 0.267859 | 0.276850 | 0.289810 | 0.290419 | 0.277811 | 0.268722 | -3.087% | -2.936% | -7.471% |
| 2048 | 0.365924 | 0.353187 | 0.359971 | 0.350372 | 0.368963 | 0.345027 | 0.353171 | 0.343666 | -2.696% | -1.914% | -0.394% |
| 4096 | 0.571044 | 0.531589 | 0.570613 | 0.517988 | 0.571558 | 0.519092 | 0.559525 | 0.518533 | -2.456% | +0.105% | -0.108% |

Versus retained: Mega candidate/baseline GM 0.994068; 5/13 lower. All104 CONTROL configs and requested knobs match; 45/104 split selections change.

Versus intermediate: Mega candidate/baseline GM 0.993925; 6/13 lower. All104 CONTROL configs and requested knobs match; 30/104 split selections change.

Versus fc1: Mega candidate/baseline GM 0.989422; 7/13 lower. All104 CONTROL configs and requested knobs match; 20/104 split selections change.

Local bytes: {'retained': [0], 'intermediate': [0], 'fc1': [0], 'candidate': [0]}. Phase wall: {'retained': 899.7906088150012, 'intermediate': 315.12906166800167, 'fc1': 318.88031805000355, 'candidate': 313.15088732299773}. The retained baseline includes its first native build; phase wall is not a kernel speedup.
