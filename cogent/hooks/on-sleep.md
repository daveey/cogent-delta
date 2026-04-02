# On Sleep

Cogamer-specific sleep hook. Runs before the platform commits, pushes, and shuts down.

## Steps

1. **Write session log** — If any improvement work was done this session, write a session log to `cogent/memory/sessions/YYYYMMDD-NNN.md` following the format in `cogent/MEMORY.md`. Skip if no improvement work was done.

2. **Update approach state** — Write current `approach_stats` to `cogent/state.json`.

3. **Fold stale learnings** — If any entries in `cogent/memory/learnings.md` have already been incorporated into `docs/strategy.md`, remove them.

4. **Summarize if needed** — If there are 5+ session logs without a covering summary, write one to `cogent/memory/summaries/weekly-YYYYMMDD.md` and clean up old session logs per `cogent/MEMORY.md` cleanup rules.
