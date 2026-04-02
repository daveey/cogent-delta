# On Wake

Cogamer-specific wake hook. Runs after the platform has already loaded identity, memory, and todos.

## Steps

1. **Read approach state** — Read `cogent/state.json` to understand PCO vs design attempt history.

2. **Check tournament standing** — Run leaderboard commands from `docs/cogames.md` to see current rank and recent matches.

3. **Report status** — Brief summary:
   - Current scores / ranking
   - Top priorities from todos
   - Recommended next action

4. **Wait for direction** — Don't start improving automatically. Present the status and let the user decide what to do next.
