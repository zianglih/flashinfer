# Typed SF ownership follow-up

Same ownership and linear-eligibility proof as `../sf-payload-linear-guard/DESIGN.md`. The only additional repair explicitly casts the computed SF row to Int32 so the DSL setup/K-loop variable merge has a consistent type. Unsigned values remain limited to nonnegative payload ownership and bank-selection indices.

Kernel `dac7f44c8203c364a4bb0b2f945f5508ca1f4d97df35405582b9380a1be46812`; patch `7ef957625147f370697511557b04d31c1386614fd1140c1dc743018800555216`. One active unstaged local source copy, based on475. Full23-case exact/SASS gate is required before timing. No sanitizer.
