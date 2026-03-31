---
name: coach.dashboard
description: Generate an HTML training dashboard from .coach/ state showing experiments, scores, learnings, TODOs. Pulls live tournament status. Opens in browser. Use for "dashboard", "training status", "show progress".
---

# Coach Dashboard

Generate a self-contained HTML dashboard from `.coach/` state.

## Steps

1. **Read IMPROVE.md** for game-specific commands (leaderboard, submissions, scoring).

2. **Read coach state**:
   - `.coach/state.json` — scores, rank, sessions, policy name, season
   - `.coach/session_config.md` — policy name, season(s)
   - `.coach/todos.md` — TODOs and dead ends

3. **Pull live tournament status**:
   - Run the leaderboard/submissions commands from IMPROVE.md
   - Fetch Observatory page if URL available
   - Get current rank, score, matches for each version across all seasons

4. **Scan session logs** (`.coach/sessions/*/log.md`):
   - Extract: timestamp, what was tried, result, score, PCO signals
   - Build experiment timeline

5. **Generate HTML** at `~/.agent/diagrams/coach-dashboard.html`:
   - **Hero KPIs**: rank, best score, sessions, gap to next
   - **Score chart** (Chart.js): one line per season, versions on x-axis
   - **Version table**: all submitted versions across all seasons with scores, filterable by season
   - **Experiment log**: sessions with change, result badge, signals
   - **Beliefs & learnings**: key insights from logs
   - **Dead ends**: from todos.md
   - **Active TODOs**: current priorities

6. **Open in browser**: `open ~/.agent/diagrams/coach-dashboard.html`

## Design

Catppuccin Mocha palette (dark-first). Chart.js for graphs. Season tabs for filtering. Responsive grid. Light/dark themes.
