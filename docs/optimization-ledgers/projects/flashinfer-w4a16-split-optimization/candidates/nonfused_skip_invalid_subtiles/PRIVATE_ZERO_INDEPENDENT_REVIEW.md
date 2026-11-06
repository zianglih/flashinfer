# Private zero-route helper review

PASS for source correctness at helper SHA256
`a4d8b3a239492609e5fb7aa48773077c9b316bbfaed6d41a7b3cbd14283aef18`.
This is a read-only review; no imports, compilation or GPU operation occurred.

- The helper verifies both imported module paths belong to the requested repo,
  records helper/source hashes, and retains partial/error state. It refuses to
  overwrite an existing result.
- It calls the existing route-boundary test with its tail-one geometry and
  unchanged reference. That test checks actual combined tactic membership.
  The four cases cover GEMM2 M128/N64/C2 and M256/N128/C2, each with PDL off/on.
- The launch wrapper changes only PDL. The private wrapper intercepts only
  ordinary GEMM2 and invokes the saved actual `_run_grouped_gemm`. It replaces
  output with a fresh BF16 sentinel17 allocation and metadata with expert0,
  limit0 and one active tile. All other actual tensors/scalars are preserved.
  This admits a physical route tile with D0, rather than making an empty launch.
- Synchronization and exact sentinel comparison happen before invoking the
  legitimate private call with its original kwargs. The unchanged public test
  then checks the legitimate result. One probe per case, all four oracle passes,
  unchanged source hashes and explicit completion are required.
- The helper itself has no timeout. `PRIVATE_ZERO_PROTOCOL.md` correctly requires
  an outer timeout because a broken final ACC release could hang synchronization;
  timeout or missing completion is failure. The PDL cases test execution, not
  demonstrated overlap or performance.

No concrete source blocker found. Actual D0 progress, absence of output writes
and normal-call numerical correctness remain runtime evidence to be supplied by
the sole executor.
