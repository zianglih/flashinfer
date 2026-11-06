# Bound gather SF completion arrivals to static owners

Baseb139, activeunstagedsourceflashinfer-gather-sf-arrivals-review. The local gatherbarrier currentlyexpects129arrivals: onepayloadbytearrival plus128SFcopyarrivals. For routeN16/32/64 onlyNthreads caneverissueSFcopies; sf_row is a bijection0..127 and every laterSFrowblock adds128. DynamicMMAroundedN neverexceedsrouteN. Set count1+min(routeN,128) and predicate onlytheSFnoincarrival on sf_row<routeN. All4payloadGather4warps remainactiveandtheirfulltransactionbytesunchanged. WideN128/256retains129; no dynamicparticipantcountornewknob.

The earlier gather-sfb-live-rows optimization kept129arrivals as scopeisolation. This is a distinct completion-participant experiment. PreserveSFcopyzero-fill/roundedextent, separatepayloadtxbytes, relayrelease/acquire, operandreusestages and all tails. Excludedthreads havenopendingSFcopies in any iteration, includingempty/partialroutes andKtails. Participants stillarrivewhenalltheiractualcopiesarepredicatedoff.

Source-countproof enumeratesalllegalrouteN,CTA1/2 and everyvalidN. Scopedprecommitpassed. Next39existingexact withprelaunchmatchedb139resourceguards; verifycandidatePTXbarrierinitialcountsand predicatedcp.asyncarrivals, FC2binaryidentityandwidecodegen. OnlythenboundedCAACnarrowdecodepluswidecontrols. No sanitizerorW4change.
