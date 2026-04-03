# gamma — Session Memory

## Key Learnings (20260403)

### Four_score Optimization Pattern
- **Conservative adjustments work**: Hotspot penalty +50%, scrambler -50 steps both succeeded
- **Aggressive changes fail**: Network bonus 3×, LLM prescriptive rules, threat_bonus +50% all regressed significantly
- **Balance is critical**: Over-indexing on any single parameter (defense, consolidation, offense) disrupts equilibrium
- **High variance**: Same policy can score 4.55-19.86 across seeds due to multi-team dynamics

### Successful Improvements
1. **Hotspot penalty** (004): 8→12 base, 5→6 mid → +49.7%
2. **Early scrambler** (007): step 100→50 → +7.84%
3. **Cumulative**: 6.03 → 9.74 per cog (+61.5%)

### Failed Patterns
- Defensive over-tuning (threat_bonus +50%): -17.04%
- Clustering over-priority (network bonus 3×): -64.2%
- Role switching chaos (LLM prescriptive): -41.6%
- Premature pressure (30→15 steps): -5.97%

### Auth Blocker
- COGAMES_TOKEN exists in secrets store but not in container environment
- MCP get_secrets returns key names only, not values (security)
- Cannot upload policy to dashboard until container restart
- Season mismatch discovered: optimizing four_score but only beta-cvc (machina_1) exists for freeplay

## Current Session (20260403 continued)
- Testing improvement 011: teammate penalty 6→9 for 4-team coordination
- **Critical constraint discovered**: CPU testing extremely slow (50+ min/seed for 32-agent four_score)
  - Baseline eval: 48+ minutes elapsed (23 min CPU time), still running, NO GAME OUTPUT YET
  - Test seed 42: 40+ minutes elapsed (17 min CPU time), still running, NO GAME OUTPUT YET
  - Projected completion: 50-60+ min per seed (still uncertain, no completion yet)
  - Full 5-seed validation would take ~250-300+ minutes (4-5+ hours)
  - **30min improvement loop completely non-viable with current test protocol**
  - **CRITICAL: Even single-seed validation (~50-60min) doesn't fit 30min loop**
  - **Alternative needed: GPU access or accept multi-hour improvement cycles**
- Parallel session tested improvement 012 (LLM teammate awareness): **FAILED** with +3.8% avg but 40% catastrophic failure rate (variance 22.14). LLM role suggestions trigger pathological behavior.
- Auth resolved: cogames authenticated, can upload
- Scheduled loops: 10min tick, 30min improve (needs major adjustment or alternative approach)

## Next Session
- Check 011 results (tests running in background)
- Consider shorter test protocol or GPU access for faster iteration
- Upload validated improvements to beta-four-score (if season exists) or beta-cvc
