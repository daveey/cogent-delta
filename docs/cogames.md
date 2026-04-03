# CoGames CLI

## Setup

See `cogent/skills/cogames.md` for install, auth, and validation steps.

## Running Locally

### Machina_1 (2 teams, 8 agents each = 16 total)

```bash
ANTHROPIC_API_KEY= PYTHONPATH=src/cogamer cogames play -m machina_1 \
  -p class=cvc.cogamer_policy.CvCPolicy \
  -c 8 -r none --seed 42
```

### Four_Score (4+ teams, 8 agents each = 32 total)

**Self-play** (4 copies of your policy):
```bash
ANTHROPIC_API_KEY= PYTHONPATH=src/cogamer cogames play -m four_score \
  -p class=cvc.cogamer_policy.CvCPolicy \
  -c 32 -r none --seed 42
```

**Mixed policies** (test vs others):
```bash
ANTHROPIC_API_KEY= PYTHONPATH=src/cogamer cogames play -m four_score \
  -p class=cvc.cogamer_policy.CvCPolicy \
  -p alpha.0 \
  -p alpha.0 \
  -p alpha.0 \
  -c 32 -r none --seed 42
```

**Test across 5+ seeds** (42–46) and average. Single-seed results are noise.

## Deploying

### Prerequisites

Run `cogent/skills/cogames.md` if not already done.

### Upload to Season

Upload a policy to a season. Use the cogent name from `cogent/IDENTITY.md` as the policy name (`-n`). Must run from `src/cogamer/`:

```bash
cd src/cogamer && PYTHONPATH=. cogames upload \
  -p class=cvc.cogamer_policy.CvCPolicy \
  -n <cogent-name> \
  -f cvc -f setup_policy.py \
  --setup-script setup_policy.py \
  --season <season> \
  --skip-validation
```

`setup_policy.py` runs on the remote server to install `anthropic[bedrock]` for LLM calls.

### Validate Before Upload

Always test locally across 5+ seeds before uploading.

**For four_score (current focus):**
```bash
for seed in 42 43 44 45 46; do
  echo "=== Seed $seed ==="
  ANTHROPIC_API_KEY= PYTHONPATH=src/cogamer cogames play -m four_score \
    -p class=cvc.cogamer_policy.CvCPolicy \
    -c 32 -r none --seed $seed | grep "per cog"
done
```

**For machina_1:**
```bash
for seed in 42 43 44 45 46; do
  ANTHROPIC_API_KEY= PYTHONPATH=src/cogamer cogames play -m machina_1 \
    -p class=cvc.cogamer_policy.CvCPolicy \
    -c 8 -r none --seed $seed | grep "per cog"
done
```

If average score drops vs baseline, do NOT upload — revert the change first.

## Monitoring

```bash
cogames leaderboard <season> --mine       # standings
cogames matches --season <season>         # recent matches
cogames match-artifacts <match-id>        # logs from a match
cogames season progress <season>          # stage progression
```

## Seasons

| Season | Mission | Purpose | Format |
|--------|---------|---------|--------|
| `beta-four-score` | four_score | **Freeplay** — multi-team testing | Self-play qualifier → matches vs random opponents |
| `beta-cvc` | machina_1 | **Freeplay** — 2-team testing | Self-play qualifier → 20 matches vs random partners |
| `beta-teams-tiny-fixed` | machina_1 | **Tournament** — ranked competition | Multi-stage elimination, team-based scoring |

**Current focus**: `beta-four-score` — validate improvements in 4-team format before tournament.

Freeplay policies qualify via self-play, then play matches against random opponents. Use this to validate changes against diverse opponents before committing to tournament.

Tournament format: multi-stage elimination. Policies qualify via self-play, get seeded into teams, teams compete across progressive stages with culling. Final score based on team rank.

## Learnings & Experience

Games write experience to `/tmp/coglet_learnings/{game_id}.json` containing snapshots, LLM logs, and per-agent state. Use these for PCO epochs.
