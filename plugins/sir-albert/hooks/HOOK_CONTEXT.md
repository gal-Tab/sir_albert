## sir_albert — session start

**Use-the-skill rule:** for task work — exploring or designing an idea, planning, executing a plan, debugging, shipping a branch, handing off — invoke the matching skill below with the Skill tool *before any other response*, including clarifying questions (the skill asks them better). When the sir-albert router names a skill, invoke it.
If the task needs more than ~3 steps and no plan exists yet, invoke `/sir-albert:plan` first — unless rigor is fast (`os/rules/rigor.md`).
Not reasons to skip: "it's simple", "I need context first", "I know what the skill says".
Skip only for chit-chat, one-line factual answers, or when no row fits — never invoke a skill just to have invoked one. A question *about* skills (what one does, which exist) is not a request to create or edit one.

**Core skills** (sir-albert first):
| Need | Skill |
|------|-------|
| Explore / attack an idea | `/sir-albert:brainstorm` |
| Spec → plan | `/sir-albert:plan` |
| Run a plan | `/sir-albert:execute` |
| Debug a system | `/sir-albert:debug` |
| Ship a branch | `/sir-albert:build` |
| Write a handoff | `/sir-albert:handoff` |
| Reload last handoff | `/sir-albert:resume` |
| Make / recall a decision | `/sir-albert:decide` |
| Scope-lock edits | `/sir-albert:freeze` |
| Create or edit a skill | `/sir-albert:create-skill` |

Map: `os/RESOLVER.md`
Active packs: {PACK_LIST}
{RESUME_HINT}