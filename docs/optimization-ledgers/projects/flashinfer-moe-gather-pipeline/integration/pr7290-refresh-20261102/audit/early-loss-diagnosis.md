# Early W4A16 prefill-loss diagnosis

The original CAAC results remain unchanged. K3 EP4096 reports −6.17%; N3U EP16384 reports −5.79%.

- All nine completed jobs have identical observed CUDA resources and static pipeline configurations across the four phases. Both target W4 pairs load FC1 with 96 initial registers / 640-thread bound, FC2 with 128 registers / 512-thread bound, and zero local bytes. Exact selected tactics and routes are preserved.
- The losses emerge during the measurement windows. K3 first-25-sample medians are 531.492/531.813/533.572/537.380 microseconds in CAAC order, yielding +0.33% for the candidate. Later candidate quartiles show 1777/1710 MHz while the controls report 2032 MHz. Some control later quartiles also slow despite the reported clock, so NVML readings alone do not explain every sample.
- N3U first-25 medians are 1334.468/1354.212/1343.876/1348.772 microseconds, yielding −0.55%. Later phases vary between 1312 and 2032 MHz and include clock-event mask 4. The first-quartile FC1, FC2, and combine differences are each around half a percent, instead of the full-window multi-percent loss.
- These fixed first-quartile diagnostics are not substituted for the original 100-sample medians. They expose a hardware/timing confound requiring a matched-clock repeat before source attribution. No GPU run or source change was made by this audit.

## Weight bytes and codegen boundary

The unchanged weight-preparation helper uses global scale 1.0, standard NVFP4, swizzled scales, and fully aligned rows/columns for these models. Upstream native quantizer changes alter scheduling, padded writes, and placement of the scale read after PDL; the reciprocal hoist operates on 1.0 here. No valid-element numerical change is apparent from source. That is not a byte-comparison result; a direct prepared-weight hash comparison remains the conclusive test if needed.

Kernel resources match, but this does not prove SASS identity. Loaded W4 symbols are generic and identical across configurations, so mapping a specific cached cubin requires compile metadata or comparison of an offline cache snapshot. Runtime validation is coordinating that without changing the running campaign.
