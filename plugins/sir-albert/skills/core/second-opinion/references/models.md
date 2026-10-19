# Model router — second-opinion

Source of truth for role to model. Keyed by role, not model name. Change only when Gal says so, and only through `/sir-albert:create-skill` (it is a skill edit).

| Role | Model | Effort | Used for |
|---|---|---|---|
| consult (default) | `gpt-6.1-sol` | `high` | plan review, second opinion, open questions |
| deep | `gpt-6.1-sol` | `xhigh` | Gal says "deep" / architectural review |
| quick | `gpt-6-luna` | `medium` | cheap sanity check, "quick look" |

Invoked as `-m <model> -c model_reasoning_effort="<effort>"`.

Known catalog slugs (seen 2026-10-19): `gpt-6.1-sol`, `gpt-6-sol`, `gpt-6-astra`, `gpt-6-luna`, `gpt-5.6-sol`, `gpt-5.6-terra`, `gpt-5.6-luna`. Hidden (`visibility: hide`) slugs are ignored.

## Pre-flight (run before every call)

Catalog is live: `/opt/homebrew/bin/codex debug models` (JSON `{"models": [{slug, visibility, supported_reasoning_levels}]}`). Pass the router's model and effort:

```bash
/opt/homebrew/bin/codex debug models 2>/dev/null | python3 -c '
import json, re, sys
want, effort = sys.argv[1], sys.argv[2]
KNOWN = {"gpt-6.1-sol","gpt-6-sol","gpt-6-astra","gpt-6-luna","gpt-5.6-sol","gpt-5.6-terra","gpt-5.6-luna"}
ms = [m for m in json.load(sys.stdin)["models"] if m.get("visibility") == "list"]
lv = lambda m: {r["effort"] if isinstance(r, dict) else r for r in m.get("supported_reasoning_levels", [])}
by = {m["slug"]: m for m in ms}
def sol_key(s):
    v = re.match(r"gpt-([\d.]+)-sol$", s)
    return tuple(int(x) for x in v.group(1).split(".")) if v else None
if want in by and effort in lv(by[want]):
    print(f"OK model={want} effort={effort}")
else:
    sols = sorted((s for s in by if sol_key(s)), key=sol_key)
    if not sols:
        print("FAIL no listed *-sol model in catalog"); sys.exit(1)
    fb = sols[-1]
    eff = effort if effort in lv(by[fb]) else "high"
    print(f"FALLBACK requested={want}/{effort} model={fb} effort={eff}")
new = sorted(set(by) - KNOWN)
if new: print("DRIFT new model(s) available, router unchanged: " + ", ".join(new))
' gpt-6.1-sol high
```

Output handling:
- `OK` — run with the router values.
- `FALLBACK` — run with the printed model/effort and tell Gal which model actually ran and why.
- `FAIL` or no output — stop and tell Gal the catalog is unavailable; do not guess a model.
- `DRIFT` line — pass it to Gal as a one-line note. Never edit this table on your own.

The Codex client may lag the catalog (0.159.2 vs 0.163.0 seen). The account serves the catalog, so new models appear regardless. Update the client only if a model needs a newer one.
