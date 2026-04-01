# Session 49 Log

**Timestamp**: 2026-04-01 04:00:00
**Approach**: IntelligentDesign

## Status: DONE (no improvement)

No changes kept. Known_junctions consistency fix caused extreme variance.

## Tournament Update
- Stage 1 complete (26→16 policies survived)
- Stage 2 running (two-player play-ins, 17.6% complete)
- Our versions with improvements (v67-v73) scored 8.84 in stage 1 (best observed)

## Change Attempted
Fixed inconsistency: `_preferred_alignable_neutral_junction` used `_world_model.entities` for neutral/enemy junctions while `_nearest_alignable_neutral_junction` used `_known_junctions`. Changed preferred to also use `_known_junctions`.

Result: +40.8% average but driven by single outlier (seed 43: 10.70) while two seeds hit 0.00. Extreme variance. Also a no-op in freeplay (single agent = same data sources). Reverted.

## Dead End
- known_junctions consistency in preferred scoring: extreme variance, no-op in freeplay
