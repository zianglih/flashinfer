# Deferred SF address formation: no improvement

This liveness-only repair forms Int64 SF offsets and shared offsets after the payload coordinate cache. It does not change ownership, guards, register budgets, tactics or pipeline behavior.

The four targeted N256/oneCTA/K4 modes pass exact assertions. Both FP4 payload cases still have8B stack and8/5LDL plus1STL sites. Seven of eight FC1/FC2 cubins are byte-identical to V1, including one of the spilled FP4 kernels; the remaining binary has the same spill counts. No timing was run.

Source kernel `01f0954168fb59a4fcc7ac76c26d7c4c82864ad0d1759f8242f231e72d3a43a0`, patch `b4b2986540a8b8440eceb47dfa0b9ea5d9184f3cb416677485fa95953c36a686`. Archive SHA `3f91e922fd146c16785bdb63ec2d528ee5e4c2ded0986f7ef629849bf7fcc0bb`,37 files. The current review copy has moved to the separately recorded linear-bound/unsigned-mapping follow-up; this remote source/evidence is frozen.
