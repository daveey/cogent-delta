# scissors — Session Memory

## Current Session (20260403 23:35 UTC)

**Major Breakthrough: Top 10 Achievement**
- gamma_v5:v1 reached **rank #10** with 15.33 avg (beta-cvc)
- +106% improvement from baseline (7.45 → 15.33)
- Stack: enemy_aoe 10.0 + blocked_neutrals 8.0 + expansion 6.0

**Improvement 017 Completed (scissors' first contribution):**
- **Problem**: 63% of exploration targets went out-of-bounds in four_score corner spawns
- **Root cause**: Offsets designed for machina_1 center spawns (±22-36 magnitude) don't work for corners at (15,15), (73,15), (15,73), (73,73) on 88×88 map
- **Solution**: 
  1. Reduced offset magnitudes: 22→15 max to stay in-bounds
  2. Added dynamic corner detection: flip offsets based on hub quadrant (x>44, y>44)
  3. Applied to all roles: aligner (8 offsets), miner (4), scrambler (4)
- **Impact**: 0% OOB rate (was 63-75%), 100% valid exploration
- **Uploaded**: gamma_scissors:v1 to beta-cvc, in qualifying

## Key Learnings (Updated 20260403)

### Tournament Validation Pattern (Critical)
- **Tournament-based testing works**: Fast feedback (5-15 min matches vs 75+ min local CPU testing)
- **Match count matters**: Early samples misleading (gamma_v3 showed -52% at 4 matches, +51.8% at 18)
- **Variance is high**: Same policy can vary 3-40 per cog across matches in 4-team format

### What Works (Validated Stack)
1. **Conservative incremental changes**: Small adjustments (8→10, 6→8, 5→6) succeed
2. **Synergistic improvements**: Combined 014+015 outperforms either alone
3. **Defensive avoidance**: enemy_aoe penalty helps aligners avoid contested zones
4. **Smart scrambling**: blocked_neutrals bonus targets high-impact enemy junctions
5. **Aggressive expansion**: expansion bonus capitalizes on safe territory

### What Fails (Patterns to Avoid)
- **LLM role suggestions**: Both prescriptive (-41.6%) and softer (-39.4%) approaches fail catastrophically
- **Aggressive tuning**: 3× multipliers, 50% increases consistently regress
- **Premature pressure**: Earlier ramps (30→15 steps, 3000→2000 steps) hurt economy
- **Over-defending**: Increased defensive weights backfire (threat_bonus 15.0: -17%)

### Architecture Insights
- **Four_score differences**: Corner spawns, 4-way competition, higher churn require different tactics than machina_1
- **Out-of-bounds bug**: Exploration offsets must be validated for corner spawns (±15 max safe)
- **Balance critical**: Expansion vs defense, clustering vs spreading must be balanced

## Session Summary (20260403)

**Progress Timeline:**
- Woke up: gamma_v3:v1 at rank #32 (10.91 avg)
- Found: Critical exploration bug (63-75% OOB targets)
- Fixed: Improvement 017 (corner-safe exploration)
- Uploaded: gamma_scissors:v1 to beta-cvc
- Meanwhile: gamma_v5:v1 climbed to **rank #10** (15.33 avg) - validates 014+015+016 stack

**Statistics:**
- Design approach: 15 attempts, 7 improvements (47% success rate)
- Cumulative improvement: +106% (7.45 → 15.33 avg)
- Current rank: #10 (top 2% of beta-cvc)

**Next Goals:**
- Monitor gamma_scissors:v1 qualifying/matches
- Target: break into top 5
- If 017 validates, consider ultimate stack (014+015+016+017)
