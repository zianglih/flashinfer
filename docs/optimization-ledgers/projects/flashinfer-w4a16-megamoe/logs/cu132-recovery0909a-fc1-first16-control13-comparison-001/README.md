# FC1 first16 complete CONTROL100 screen

Complete fixed CONTROL100 screening on hu-pdx-115. Candidate auto is unrun. The FC1 change modifies shared and private Mega files over neutral e359; retained38870 remains a separate comparison. Shared split source changes too. Unbracketed rows are preserved without minima or drift adjustment; no promotion from this arithmetic report.

| Tokens | Retained split ms | Retained Mega ms | Intermediate split ms | Intermediate Mega ms | FC1 split ms | FC1 Mega ms | FC1 vs retained | FC1 vs intermediate |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 0.078321 | 0.093409 | 0.091025 | 0.097713 | 0.084880 | 0.088193 | -5.584% | -9.743% |
| 2 | 0.118209 | 0.117889 | 0.114929 | 0.130209 | 0.115393 | 0.129825 | +10.125% | -0.295% |
| 4 | 0.151617 | 0.138209 | 0.144929 | 0.133649 | 0.150738 | 0.140321 | +1.528% | +4.992% |
| 8 | 0.177538 | 0.156386 | 0.171073 | 0.158305 | 0.169809 | 0.166450 | +6.435% | +5.145% |
| 16 | 0.191154 | 0.198770 | 0.189282 | 0.187634 | 0.194898 | 0.185634 | -6.609% | -1.066% |
| 32 | 0.219602 | 0.222435 | 0.219794 | 0.213634 | 0.208770 | 0.219170 | -1.468% | +2.591% |
| 64 | 0.228482 | 0.243602 | 0.234178 | 0.243410 | 0.226834 | 0.235587 | -3.290% | -3.214% |
| 128 | 0.257842 | 0.250066 | 0.247331 | 0.249938 | 0.243107 | 0.250658 | +0.237% | +0.288% |
| 256 | 0.261491 | 0.257570 | 0.260177 | 0.254786 | 0.256115 | 0.260562 | +1.162% | +2.267% |
| 512 | 0.256355 | 0.252083 | 0.251266 | 0.258323 | 0.255810 | 0.264466 | +4.912% | +2.378% |
| 1024 | 0.273970 | 0.277282 | 0.267859 | 0.276850 | 0.289810 | 0.290419 | +4.738% | +4.901% |
| 2048 | 0.365924 | 0.353187 | 0.359971 | 0.350372 | 0.368963 | 0.345027 | -2.310% | -1.526% |
| 4096 | 0.571044 | 0.531589 | 0.570613 | 0.517988 | 0.571558 | 0.519092 | -2.351% | +0.213% |

Versus retained: Mega candidate/baseline GM 1.004695; 6/13 lower. All104 CONTROL configs and requested knobs match; 45/104 split selections change.

Versus intermediate: Mega candidate/baseline GM 1.004551; 5/13 lower. All104 CONTROL configs and requested knobs match; 30/104 split selections change.

Local bytes: {'retained': [0], 'intermediate': [0], 'candidate': [0]}. Phase wall: {'retained': 899.7906088150012, 'intermediate': 315.12906166800167, 'candidate': 318.88031805000355}. The retained baseline includes its first native build; phase wall is not a kernel speedup.
