# 04a — Hebrew pattern mining (CHECKPOINT: Gal approves list)

**Blocked by:** —
**Spec:** `docs/specs/2026-09-24-w3-router-design.md` §Component 2 — Hebrew patterns

## Goal

Mine real Hebrew prompts from Gal's session transcripts to derive intent-based router patterns. Do not guess; use actual usage.

## ⚠ CHECKPOINT — Gal approves the pattern list before it enters router_data.json

The mined phrases and proposed patterns are presented for review. Nothing is written to `router_data.json` until Gal says yes.

## Steps

1. Run the miner (Python script or one-liner):
   ```python
   import json, glob, re
   files = glob.glob(os.path.expanduser("~/.claude/projects/**/*.jsonl"), recursive=True)
   # Skip subagent transcripts
   files = [f for f in files if "/subagents/" not in f]
   hebrew_re = re.compile(r'[֐-׿]')
   prompts = []
   for f in files:
       for line in open(f, encoding="utf-8", errors="ignore"):
           try:
               msg = json.loads(line)
               # User messages only
               if msg.get("role") == "human" or msg.get("type") == "user":
                   text = msg.get("content", "")
                   if isinstance(text, list):
                       text = " ".join(b.get("text","") for b in text if isinstance(b,dict))
                   if hebrew_re.search(str(text)):
                       prompts.append(str(text)[:200])
           except: pass
   print(f"Found {len(prompts)} Hebrew prompts")
   for p in prompts[:100]: print(repr(p))
   ```
2. Review the output. Group by apparent intent (brainstorm, plan, debug, handoff, etc.).
3. Propose a phrase pattern for each intent that has ≥2 real examples. Format:
   ```
   Intent: grill
   Examples: "חקור אותי על...", "תשאל אותי שאלות על..."
   Pattern: r'\b(חקור אותי|תשאל אותי)\b'
   ```
4. **Present the list to Gal for approval.** Do not write to `router_data.json` yet.
5. After approval: add approved patterns to `"hebrew_patterns"` array in `router_data.json` (same `{order, intent, pattern, nudge}` shape, merged with English patterns in order).

## Definition of Done

- [ ] Miner ran, Hebrew prompts extracted
- [ ] Proposed patterns cover at least 3 intents with real examples
- [ ] **Gal has reviewed and approved the list** (this is the CHECKPOINT)
- [ ] Approved patterns added to `router_data.json`
- [ ] English and Hebrew patterns interleaved by `order` field
