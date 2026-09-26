# 04a Hebrew Pattern Mining — Results

**Date:** 2026-09-25  
**Files scanned:** 361 main transcripts (~102,595 JSONL lines, excluding /subagents/)  
**Hebrew prompts found:** 24  
- 14 identical create-skill test prompts (not organic)  
- 10 pasted/injected content  
- **Organic Hebrew process-skill requests: 0**

## Approved patterns (Gal-approved 2026-09-25)

| order | intent | pattern | nudge |
|-------|--------|---------|-------|
| 200 | slack-hebrew | `(?=.*(?:כתוב\|נסח))(?=.*סלאק)` | `→ /sir-albert:slack-in-my-voice` |
| 210 | linkedin-hebrew | `(?=.*(?:כתוב\|נסח))(?=.*פוסט)(?=.*לינקדאין)` | `→ /sir-albert:linkedin-in-my-voice` |

Note: `\b` word boundaries don't apply to Hebrew; lookaheads used instead.

No speculative patterns added. Zero organic process-skill requests found.
