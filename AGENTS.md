# AGENTS.md

Instructions for AI agents working with this repository.

## Cogent Lifecycle

Every session should start with `/wakeup` and end with `/sleep`.

## Skills

- **`/initialize`** — First-time setup. Creates `.cogent/IDENTITY.md` via RPG-style character creation. Required before any other skill works.
- **`/wakeup`** — Restores the cogent from `.cogent/` state. Reads identity, memory, todos, and tournament standing. Reports status and waits for direction.
- **`/sleep`** — Persists session state. Writes session logs, updates learnings and todos, commits and pushes `.cogent/`.
- **`/improve`** — One improvement iteration: analyze code, implement a change, test across seeds, auto-submit if improved.
- **`/proximal-cogent-optimize`** — PCO cycle: play a game, collect experience, LLM proposes patches, test, submit.
- **`/dashboard`** — Generate HTML dashboard from `.cogent/` state showing experiments, scores, and learnings.
- **`/memory-wipe`** — Nuclear reset of memory and state. Identity survives.

## Docs

- [docs/coglet.md](docs/coglet.md) — Coglet framework: COG/LET primitives, mixins, runtime
- [docs/architecture.md](docs/architecture.md) — Policy architecture, program table, PCO, alpha.0 reference
- [docs/strategy.md](docs/strategy.md) — What works, what to try, dead ends, learnings
- [docs/rules.md](docs/rules.md) — Game rules, constants, team coordination
- [docs/cogames.md](docs/cogames.md) — CLI setup, running, uploading, monitoring
- [docs/tools.md](docs/tools.md) — Development rules & constraints
