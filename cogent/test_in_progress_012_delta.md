# Test In Progress: 20260404-012-delta

**Status**: Testing across seeds 42-46
**Started**: 2026-04-04 00:15 UTC
**Output**: test_results_012_delta.txt

## Change

**Focus**: Scrambler corner_pressure divisor adjustment

**File**: `src/cogamer/cvc/agent/scoring.py` - line 143

**Description**: 
Adjusted scrambler `corner_pressure` divisor from 8.0 to 7.0 (~14% increase). This makes distant enemy junctions moderately more attractive to scramblers for better disruption of expanding opponents in 4-team format.

**Hypothesis**: In four_score with 4 corner teams, current divisor 8.0 may slightly under-weight distant disruption. Conservative 8.0→7.0 adjustment could improve enemy expansion blocking.

## Baseline

Current baseline: **9.74 avg per cog** (from attempt 007: early scrambler activation)
- Seeds 42-46: 9.37, 11.44, 19.86, 2.64, 5.38

## Results

**Seed 42**: 5.42 per cog (baseline: 9.37) → **-42.2% regression**
**Seed 43**: Running...
**Seeds 44-46**: Pending

**Test INVALIDATED**: Change was overwritten by concurrent development

During test execution, scoring.py was modified by another agent (attempt 023: hub_penalty mid-tier reduction). The corner_pressure change (8.0→7.0) was reverted back to 8.0.

Test results (seed 42: 5.42, -42%) are **NOT VALID** for attempt 012-delta since the code being tested no longer contains the intended change.

**Lesson**: Concurrent development on same codebase invalidates isolated testing. Delta's attempt 012-delta abandoned due to codebase conflict.
