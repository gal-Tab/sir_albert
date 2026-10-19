---
name: second-opinion
description: Use when Gal wants another model's view on a plan, diff, or open question. Triggers on "second opinion", "ask codex", "ask GPT", "have another model look at this", "review this plan with codex", "sanity check with another model".
---

# second-opinion

Boot from `os/PREAMBLE.md`.

**TLDR:** send exactly what Gal names to Codex (GPT) in a read-only, ephemeral run, then answer with "Codex/GPT says" plus your own agree/disagree per point. AUTO under `autonomy.md` because Codex can never edit or persist anything.

## Binary and auth

- Always `/opt/homebrew/bin/codex` by absolute path. The bare `codex` on PATH is an axcli gateway wrapper billed to a company budget, not Gal's ChatGPT subscription.
- Check first: `/opt/homebrew/bin/codex login status` must print `Logged in using ChatGPT`. If not, stop and tell Gal: `! /opt/homebrew/bin/codex login`. Never run login yourself.

## Safety (before any call)

1. Collect only the files or text Gal named. No extra repo content.
2. Tell Gal what leaves the machine (file paths or text, model, effort) in one line.
3. ASK first if the content could hold secrets, customer data, or HubSpot data. Redact or get an explicit yes.
4. Always `-s read-only` and `--ephemeral`. Never use `workspace-write`, `danger-full-access`, or `--dangerously-*`.

## Pick the role

Roles map to model and effort in [`references/models.md`](references/models.md). Default is **consult**. "Deep" or architectural review is **deep**. "Quick look" or cheap sanity check is **quick**.

Run the pre-flight in `references/models.md` before every call. It confirms the model is listed and the effort is supported, falls back to the newest `*-sol` if not, and prints a drift line for new models. Say which model actually ran. Never edit the router table yourself.

## Modes

Create the output file outside the repo: `OUT=$(mktemp -d)/codex-out.md`.

**Plan, spec, doc, or open question** (prompt on stdin, never as an argument):

```bash
/opt/homebrew/bin/codex exec -s read-only --ephemeral --skip-git-repo-check \
  -C <dir> -m <model> -c model_reasoning_effort="<effort>" -o "$OUT" - <<'EOF'
<frame + the text or file contents Gal named>
EOF
```

Frame for a plan: "Review the plan below. Find holes, missing steps, and wrong assumptions. Rank by severity (high/med/low), one line of reasoning each, then a short list of what you would change. Do not edit files." For an open question, replace with the question verbatim.

**Diff or code review** (run from inside the repo; `exec review` has no `-s` or `-C`, so pin the sandbox with `-c`):

```bash
cd <repo> && /opt/homebrew/bin/codex exec review -c sandbox_mode="read-only" --ephemeral \
  -m <model> -c model_reasoning_effort="<effort>" -o "$OUT" \
  --uncommitted        # or: --base <branch>  |  --commit <sha>
```

Read `$OUT` for the final message. If it is empty or the command exits non-zero, show Gal the error tail and stop; do not retry with looser flags.

## Report format

TLDR first, then per point:

| # | Codex/GPT says | Claude: agree / disagree | Why |
|---|---|---|---|

Close with the model and effort that ran, and the drift line if any. Never paste Codex output raw, and never apply its suggestions without Gal's go-ahead.

## Out of scope

Auto-editing from Codex output, multi-round Claude-vs-Codex debate, API-key OpenAI usage, updating the Codex client.
