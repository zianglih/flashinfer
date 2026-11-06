# Independent SFB remap audit

The integrated K96 N256 failures are a storage-layout issue, distinct from the
already qualified numerical update plan. The K96-disabled control passes the
same sampled failures. Tokens 256/400/512 pass; 257/272/288/384 fail precisely
when the last nominal-N256 tile uses actual N at most128.

`k-tail/k96-r1/partitions.log` prints the SDK4.8 SFB copy destination:

```
shape  (((32,16,4),1), 2, 1, W)
stride (((262144,1,8388608),0), 16, 0, 32)
```

Each copy packet contains four SF16 entries in a word. K64 stays within that
word. K96 consumes six entries and thus crosses to the next word; the native
instruction uses actual N to choose the next-word spacing. For narrow N it
expects16 byte-columns, while nominal N256 storage places the next word32 away.
The initial individual-SF view only changed indexing, not publication, so could
not repair the physical gap.

For word index `k in [0,W)` and row bank `b in {0,1}`, let `B=16` and
`wide=int(valid>128)`. The proposed destination outer strides are:

```
K word: B * (1 + wide)
N bank: B * (W - (W - 1) * wide)
```

Thus wide addresses are `B*(2*k+b)`, exactly the original mapping. Narrow
addresses are `B*(k+W*b)`: the live first bank is compact, and the unused second
bank follows it. Both are bijections over the same2W disjoint16-column packets;
the total allocation, packet count, leading copy geometry, and source addresses
are unchanged. The MMA individual-SF K mode must use `(1, K_word_stride)` so
both explicit start offsets and hardware's implicit cross-word step agree.
The MMA view's row-bank term can stay unchanged: bank1 is consumed only in the
unchanged wide case.

The layout is chosen once per routed tile, after its actual token count is
known, and remains constant throughout its reduction. Each acquired operand
stage still publishes all SFB packets before its MMA instructions. The existing
operand-ready and accumulator/operand-release protocol protects the same TMEM
region. There is no extra copy, barrier, storage, or data-dependent branch.
The condition reflects the native instruction's row-bank layout, not a model
or dtype-specific performance heuristic.

This is a source/address/lifetime proof. The scheduler agent owns compilation
and full zero-tolerance runtime qualification of the remapped candidate.
