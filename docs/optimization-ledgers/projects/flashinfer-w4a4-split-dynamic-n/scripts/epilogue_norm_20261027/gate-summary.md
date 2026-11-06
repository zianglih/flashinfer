# Norm-only exact gate and resources

64 exact source-paired replays passed. All16 kernel pairs are spill-free and use identical shared/TMEM resources. Fourteen SASS outputs are byte-identical; only uniform-NV inline FC1 changes (72→75 registers with PDL off,75→77 with PDL on). Public default uses dedicated epilogue warps; a bounded saved-native profiling check on that path is running before any timing.

No performance retention claim. Original inline implementation will be preserved if a dedicated-only variant is pursued.
