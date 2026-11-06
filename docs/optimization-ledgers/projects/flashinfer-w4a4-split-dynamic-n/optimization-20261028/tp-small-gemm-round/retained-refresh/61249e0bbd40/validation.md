B300 / CUDA 13.2 focused qualification (separate source-bound gates):

- Final `61249e0bb`: 16 exact replays per source; all 16 GEMM and two combine PTX/cubin/SASS/resource pairs identical. Eight CUDA traces verify launch geometry.
- SF epilogue `d7e5ea1c`: 96 byte-exact replays; 48 GEMM / 10 combine pairs. Blockscaled rank `659777aa`: 112 exact replays / 56 GEMM pairs. W4A16 rank `2d60c885`: eight cases and 56 graph replays per source / 12 GEMM pairs.
- Scoped and commit hooks passed. **No broad pytest or sanitizer rerun this iteration.** Historical tests remain bound to their original sources; details and raw qualification receipts are in the [validation artifact](@@VALIDATION_COMMANDS_URL@@).
