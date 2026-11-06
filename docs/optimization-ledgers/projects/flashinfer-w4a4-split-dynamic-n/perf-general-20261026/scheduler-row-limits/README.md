# Independent scheduler and row-limit composition

Base `dd266b91` contains the retained shared-release and live-prefix/bounded-grid changes. The unstaged composition appends the independent FC2 scheduler tactic and per-group live-row metadata. The only change beyond the frozen components is strict rejection of boolean `rows_per_group` in host validation; valid integer inputs and device code are identical. This source is prepared for a combined full sweep only if the independent screens justify retention. It is not retained or pushed.
