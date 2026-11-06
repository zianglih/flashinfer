# W4A16 live Gather4 groups (active, unretained)

Local source is `flashinfer-w4a16-live-groups-review`, based retained475cae6b with one unstaged kernel-file change. Fifth/last gatherWG16–19, four issuing warps,144/80/96/96/64 register roles,640threads/96launch registers, FC2, PDL, CLC/ordinary scheduling, cache policies, SMEM stage geometry and public interfaces are unchanged. No tactics or shape/model policy is added.

The retained FC1 has four cached warp-uniform IDs per physical four-row group, and issues every physical B row even when dynamic MMA N is smaller. This candidate caches one lane-held row ID per32lane bank before K. A runtime row-group loop broadcasts its four coordinates; the compile-time K64 chunk loop stays inside that loop, reusing the broadcasts across all chunks in a stage. Thus it differs from the rejected swap prototype's repeated broadcasts perKchunk, as well as having no scale-factor cp.async/relay dependency.

Live rows equal dynamic MMA's8-row-per-CTA rounding, or the physical extent for static-MMA geometries. Round those rows up to the four-issuer row grain to keep ownership simple. This never exceeds physical allocation and retains every MMA-consumed zero-filled padding row. Each issuer announces `copy_rows * (physical_stage_bytes / physical_rows / 4)` on the existing direct `PipelineTmaUmma` stage; all four arrivals remain. Multicast still partitions K64 chunks across CTA peers; two-CTA completion still accounts for both CTAs and uses the existing leader redirect. No new barrier or stage is introduced.

The full warp participates in shuffles before `elect_one`. ForN256oneCTA, two constant-index register banks are selected with a scalar condition; there is no runtime register-array index, shared ID buffer, or repeated mapping load/division inside K.

CPU proof checks33,216 geometries: static/dynamicN8..256,1/2CTA, allvalidN, K64..512,1/2/4 multicast. It establishes unique ownership, coordinate lookup, allocation bounds, full MMA row coverage and aggregate transaction counts. It does not replace GPU exact testing.

Tradeoff: four SHFLs and loop control per runtime row group can outweigh skipped gathers. The related swap experiment was negative; W4 merits only a bounded independent test because its directTMA/noSF pipeline and Kchunk reuse differ. Require existing exact tests and actual SASS/local-memory inspection before fixed-tactic timings. Reject if code complexity or dynamic overhead is unjustified. Stock-clock performance uses read-only telemetry; the earlier fixed1500MHz K3 results are diagnostic only.
