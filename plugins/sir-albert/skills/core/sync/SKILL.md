---
name: sync
description: >
  Post-merge git reconciliation in one command. Checks whether local and remote
  are in sync, reports divergence in plain language, and safely cleans up
  already-merged local branches (ask-before-delete, -d only).
  Use when the user says "sync", "/sync", "are we in sync", "are we in sync between local and git",
  "merged are we in sync", "post-merge cleanup", "reconcile git",
  "clean up merged branches", or "did the merge land".
  Domain-agnostic.
---

# Sync

**Announce at start:** "Running /sir-albert:sync to reconcile local and remote git state."

---

## 1. Boot from the OS preamble

Load `os/PREAMBLE.md` (USER identity + active rules + anti-slop / use-the-skill contract)
before proceeding.

---

## 2. Gather git state

Run all of the following in sequence and capture the output:

```bash
git fetch --prune
git status -sb
git branch -vv
git branch --merged
```

- `git fetch --prune` — updates remote-tracking refs and drops refs for deleted remote branches.
- `git status -sb` — machine-readable ahead/behind counts and working-tree cleanliness.
- `git branch -vv` — shows each local branch with its upstream and ahead/behind delta.
- `git branch --merged` — lists local branches whose tips are already reachable from the
  current branch (i.e., safely deletable with `-d`).

If the directory is not a git repo, say so and stop.

---

## 3. TLDR verdict — lead with this

Before any details, emit a single-line verdict:

- **In sync** — local HEAD matches remote upstream, working tree clean.
- **Ahead N** — local has N commits not yet pushed to upstream.
- **Behind N** — remote has N commits not yet pulled locally.
- **Diverged (ahead N / behind M)** — branches have split; a rebase or merge is needed.
- **No upstream** — current branch has no tracking branch set.

Example: `> In sync — main matches origin/main, working tree clean.`

---

## 4. Report divergence in plain language

After the TLDR verdict, provide a concise breakdown:

- **Current branch vs upstream**: ahead/behind counts and what that means.
- **Working tree**: any uncommitted changes or untracked files that could interfere.
- **Stale local branches**: list every branch returned by `git branch --merged` that is
  not the current branch and not `main`/`master`. These are candidates for cleanup.

Keep it tight — no padding prose. Use a table or bullets, not paragraphs.

---

## 5. Offer safe branch cleanup (ask-before-live)

If there are stale merged branches:

1. **List them** explicitly so the user can review.
2. **Ask for confirmation** before deleting anything. Example:

   > The following local branches are already merged and can be deleted:
   > - `feat/login-redesign`
   > - `fix/typo-header`
   >
   > Delete these with `git branch -d`? (y/n)

3. Only proceed after the user confirms.
4. Delete using **`git branch -d <branch>`** (lowercase `-d`) — this refuses to delete
   unmerged branches, which is the safety net.

**Hard rules — encode these and never violate them:**
- Only `git branch -d` (lowercase). **Never `git branch -D`** — `-D` force-deletes
  unmerged branches and is blocked by guard.sh.
- Never delete the current branch.
- Never delete `main` or `master`.
- Never force-push as part of sync.
- Never run `git reset --hard` as part of sync.
- Branch deletion is a destructive action — always list and confirm before executing.

---

## 6. Completion report

After all steps, confirm to the user:

```
Sync complete.
  Verdict: <one-line verdict>
  Branches deleted: <list | none>
  Remaining local branches: <count>
```

Do NOT commit, push, or modify any files as part of this skill.
