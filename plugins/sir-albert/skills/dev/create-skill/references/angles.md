# Angles — create-skill

## Dynamic angles by skill type (§5.1)

Hard cap: **≤4 author angles** + **≤3 judges** per run.

| Skill type | Author angles (select from these, respect cap) |
|---|---|
| **Discipline** | Pressure (time/sunk-cost/authority), Loophole-hunter, Spirit-vs-letter |
| **Technique** | Naive applier, Edge-case, Transfer (just outside the examples) |
| **Reference** | Retrieval, Application, Gap |
| **Cross-cutting (always include)** | Discoverability agent (§5.4), Structural validator (deterministic), Held-out Red-team (§8) |

Cross-cutting angles are mandatory for every run regardless of skill type. They count toward the author cap.

---

## Cap rule

- **Authors:** ≤4 total (including cross-cutting). If type-specific angles + cross-cutting exceed 4, prioritize: Red-team > Discoverability > type-specific in order listed above.
- **Judges:** ≤3. Optional model diversity (some judges on a different model) to decorrelate errors.
- **k:** 3 reps per scenario (resolved in §11).

---

## Dynamic selection guidance

Pick angles at classification time based on:

1. **Skill type** — determines the type-specific menu above.
2. **Failure mode** — "match the form to the failure" (per `superpowers:writing-skills`). Pressure angle matters most for discipline skills prone to rationalization; Gap angle matters most for reference skills with known coverage holes.
3. **Budget** — T1 smoke runs use one type-specific angle + Structural validator. T2 full panel runs the full dynamic selection up to cap.
4. **Novel domains** — when the skill covers unfamiliar territory, favor Transfer (technique) or Gap (reference) to surface blind spots.

The Discoverability agent is always run because it provides an objective, machine-checkable sub-score on the description — the one dimension neither the author nor judges can self-assess reliably.
