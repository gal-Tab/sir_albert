# P1 Router Scorecard

## Summary

| Metric | Value | Bar | Result |
|---|---|---|---|
| Precision (gate) | 95.2% (n=21) | ≥80% | PASS |
| Miss rate among non-routed task prompts (diagnostic) | 57.1% (8 of n=14 should have routed) | — | — |
| False-fire rate (gate) | 0.0% (n=8) | ≤10% | PASS |

Ambiguous rows excluded from precision denominator: 4

Fired on non-task prompt (router_match labelled `none`): 1 of 21

*The control slice is a low-power sanity check (n≈10). The real wrong-fire evidence is router_match rows labelled `none`, which precision captures.*

## Dead Routes

| Route | Corpus matches | Diagnosis |
|---|---|---|
| grill | 0 | No corpus demand — broad probes ('grill', 'interview me', 'ask me questions') hit 3 prompts of 1,938, all false positives; route is unmeasurable at current corpus size. Decision to keep or drop is Gal's. |
| zoom-out | 0 | No corpus demand — broad probes ('zoom out', 'bigger picture', 'high level', 'overview') hit 11 prompts of 1,938, all false positives; route is unmeasurable at current corpus size. Decision to keep or drop is Gal's. |
| resume | 0 | Regex-impossible — Gal types "continue" which is also his most common mid-thread reply; matching it would breach the false-fire gate. No regex fix is safe; route may need to be dropped or replaced with a context-aware signal. |
| slack-hebrew | 0 | No corpus demand — only 7 Hebrew prompts of 1,938 total; route is unmeasurable at current corpus size. Decision to keep or drop is Gal's. |
| linkedin-hebrew | 0 | No corpus demand — only 7 Hebrew prompts of 1,938 total; route is unmeasurable at current corpus size. Decision to keep or drop is Gal's. |

## Per-route breakdown

| Route | TP | FP | Precision | Note |
|---|---|---|---|---|
| handoff | 1 | 1 | — | under-powered (n=2) |
| attack | 0 | 0 | — | under-powered (n=0) |
| grill | 0 | 0 | — | under-powered (n=0) |
| slack | 0 | 0 | — | under-powered (n=0) |
| zoom-out | 0 | 0 | — | under-powered (n=0) |
| design | 0 | 0 | — | under-powered (n=0) |
| brainstorm | 8 | 0 | — | under-powered (n=8) |
| plan | 10 | 0 | 100.0% |  |
| execute | 1 | 0 | — | under-powered (n=1) |
| debug | 0 | 0 | — | under-powered (n=0) |
| build | 0 | 0 | — | under-powered (n=0) |
| resume | 0 | 0 | — | under-powered (n=0) |
| slack-hebrew | 0 | 0 | — | under-powered (n=0) |
| linkedin-hebrew | 0 | 0 | — | under-powered (n=0) |

## Ranked fix list

Routes ordered by FP count (most problematic first):

### handoff (FP=1)

Sample FP prompts: (redacted — prompt text not committed)

Suggested fix: _
