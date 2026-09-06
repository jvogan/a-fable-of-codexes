# Codex Dispatch

Read this before dispatching Codex CLI workers.

## Cost And Auth Policy

Codex can be authenticated through a ChatGPT plan or an API key. ChatGPT-plan
auth consumes plan usage and plan limits vary. API-key auth is token-priced.
Do not promise unlimited or flat-rate worker capacity. Size waves to the user's
available plan, credits, and tolerance for spend.

Useful public docs:

- <https://help.openai.com/en/articles/11369540-using-codex-with-your-chatgpt-plan>
- <https://learn.chatgpt.com/docs/pricing>
- <https://learn.chatgpt.com/docs/models>
- <https://github.com/openai/codex>

## Preflight

Run once at campaign kickoff:

```bash
codex --version
codex login status
codex exec -s read-only -m gpt-6-astra "Reply with the single word ok"
```

Record the result in `preferences.md`. The smoke test confirms the account can
reach the default model: the GPT-6 Astra rollout is staged by plan, and
Enterprise workspaces need an admin to enable it. If the model is rejected,
run the campaign on `gpt-5.6-sol` at `high` and record that. If auth fails or
limits are exhausted, route implementation work to Claude workers until the
user changes the setup.

## Worker Brief Contract

Every Codex brief must include:

- Goal and success criteria
- Branch, worktree path, and base commit
- Files/directories owned by this worker
- Files/directories excluded because siblings own them
- Repo conventions to preserve
- Verification command to run from the worktree root
- Required commit message
- Required final report schema
- Instruction not to spawn subagents unless this worker is explicitly a squad lead

Codex workers are fire-and-collect. The initial brief must be complete enough to
run without follow-up questions.

## Standard Dispatch

Use `read-only` for scouts, reviewers, and consultations. Use `workspace-write`
for writers.
Keep network on only when the task needs dependency installation, package docs,
or live research. `workspace-write` keeps `.git` read-only, so a brief that
requires a commit needs the worktree's `.git` in `writable_roots`; without it
the worker cannot create `.git/index.lock`.

`approval_policy=never` keeps the envelope fixed: anything the sandbox blocks
fails instead of asking. If a host blocks `never` for unattended runs,
`--approve-for-me` routes escalation requests through Codex's automatic
reviewer. Record that choice in `preferences.md`, since it lets a model widen
the envelope mid-run.

One writer:

```bash
codex exec --json -s workspace-write \
  -c approval_policy=never \
  -c sandbox_workspace_write.network_access=true \
  -c 'sandbox_workspace_write.writable_roots=["<worktree>/.git"]' \
  --output-schema docs/campaign-hq/schemas/worker-result.json \
  -C <worktree> \
  -o docs/campaign-hq/out/<task>.json \
  - < docs/campaign-hq/briefs/<task>.md
```

Read-only scout with live web search:

```bash
codex exec --json -s read-only \
  -c approval_policy=never \
  -c web_search=live \
  -C <repo> \
  -o docs/campaign-hq/out/<task>.json \
  - < docs/campaign-hq/briefs/<task>.md
```

`codex exec` enables web search by default, but in `cached` mode (an
OpenAI-maintained index, no live fetch), so a scout needing the live web must
set `web_search=live`. Values are `live`, `indexed`, `cached`, and `disabled`;
set it per call with `-c web_search=<mode>` or as a top-level config key.
`codex exec` has no `--search` flag; the interactive `codex` command still does.
Check `codex exec --help` for the version in use.

Second Codex home, when the user has configured one:

```bash
CODEX_HOME="<second-codex-home>" codex exec --json -s workspace-write \
  -c approval_policy=never \
  -c sandbox_workspace_write.network_access=true \
  -c 'sandbox_workspace_write.writable_roots=["<worktree>/.git"]' \
  --output-schema docs/campaign-hq/schemas/worker-result.json \
  -C <worktree> \
  -o docs/campaign-hq/out/<task>.json \
  - < docs/campaign-hq/briefs/<task>.md
```

Omit `--skip-git-repo-check` for normal campaign worktrees. A bad `-C` should
fail quickly instead of running outside the intended repo.

## Model And Effort

Three independent controls set a worker's cost and quality: the model (Codex
lists `gpt-6-astra`, then the `gpt-5.6` line: `sol`, `terra`, and `luna`), the
reasoning effort (a ladder from `low` through `medium`, `high`, `xhigh`, `max`,
and `ultra`), and any separate fast-serving tier. Not every model accepts every
effort tier: `luna` stops at `max`. `ultra` is `max` plus automatic delegation,
so a worker on `ultra` spawns its own subagents. No default shape uses it;
run it only on an explicit request, for a lead meant to fan out, never a leaf.

Match effort to difficulty instead of maxing every task. A mid tier (`medium`)
on the frontier model is a sound default: a modern frontier model is strong well
below its top tier, so reserve `xhigh`/`max` for work that earns it (thorny
architecture, deep debugging, high-stakes correctness, final arbitration, or a
task that already failed at a lower tier), and route mechanical or throughput
work to a faster variant. A cheap model on genuinely hard work produces rework,
so do not under-provision either.

Astra is the working model, and the effort tier does the routing. Every
shape the conductor calls directly runs on `gpt-6-astra`:

| Shape | Effort | Sandbox | Use |
|---|---|---|---|
| Scout | `low` | `read-only`, `-c web_search=live` for research | surveys, current APIs, advisories |
| Lead | `medium` | `workspace-write` | the default worker; runs alone or fans out |
| Consultant | `high` | `read-only` | architecture answers, design second opinions, review of a Claude worker's diff |
| Arbiter | `xhigh` | `read-only` | bake-off judging, final arbitration between a critic and an author |
| Fan-out lead | `max` | `workspace-write`, own worktree | a hard task that splits many ways; the brief tells the lead to fan out, and it plans, delegates, and returns one branch |

The default when the user has specified nothing is the lead shape. A worker on
that default may run the task alone, spawn one role, or spawn the roles the
user names. When it does fan out, the shipped roles are `feature` (`gpt-6-astra`
at `medium`) for implementation that needs judgment, `critic` (`gpt-6-astra` at
`high`, read-only) for a second opinion on a sibling's diff, and `grunt`
(`gpt-5.6-luna` at `xhigh`) for mechanical refactors, fixtures, search, and
small tests. Lead And Leaf Roles below covers the files that carry those
settings. The review gates reference has the consultant invocation.

On plan credits Astra costs 2.5x Sol, 5x Terra, and about 50x Luna per token,
and its fast tier multiplies that again. Astra finishes coding tasks in far
fewer tokens, so per-task cost lands near Sol's and the 5.6 line earns its
place only at Luna's price: the `grunt` role exists to conserve Astra usage on
work that needs no judgment. Above 272K input tokens the API adds a
long-context premium. The CLI compacts near that point unless
`auto_compact_token_limit` is raised toward Astra's 1M window, so raise it only
for a task that needs the whole window.

Precedence is the user's live request, then a task-specific policy, then
configured defaults, bounded by what the active CLI and account support. A live
request for a specific model or effort wins; do not silently "upgrade" or
"downgrade" it. Prefer per-call flags such as `-m <model> -c
model_reasoning_effort=<level>` when one task needs a different policy; do not
rewrite the user's global config unless asked. If a requested model or effort
value is unavailable, stop and record the limitation instead of pretending the
requested policy was used.

Avoid hard-coded model names in briefs unless they come from `preferences.md` or
the user just specified them. When the user specifies a model or effort policy,
write it into the brief and the fleet table.

## Lead And Leaf Roles

Subagents inherit the parent's model, reasoning effort, and sandbox policy
unless a role sets them. A role is a standalone TOML file under `.codex/agents/`
(project-scoped) or `~/.codex/agents/` (personal). Each file defines `name`,
`description`, and `developer_instructions`, and may set `model`,
`model_reasoning_effort`, and `sandbox_mode`. Built-in roles are `default`,
`worker`, and `explorer`.

- <https://learn.chatgpt.com/docs/config-file/config-reference>
- <https://learn.chatgpt.com/docs/agent-configuration/subagents>

Roles are a convenience for a worker that fans out. Bootstrap copies three of
them from the skill's `assets/codex-agents/`, and a campaign can edit them, add
roles, or ignore them. Roles are named for the job so the model behind each
can change with the next generation. Each follows the same shape:

```toml
# .codex/agents/feature.toml
name = "feature"
description = "Judgment leaf: features, bug fixes, and tests that need design care."
developer_instructions = "Own only the files named in your task. Run the verification command before reporting. Do not spawn agents."
model = "gpt-6-astra"
model_reasoning_effort = "medium"
```

| Role | Model | Effort | Sandbox | Leaf work |
|---|---|---|---|---|
| `feature` | `gpt-6-astra` | `medium` | inherited | Features, bug fixes, and tests that need judgment. Medium is Astra's default tier. |
| `critic` | `gpt-6-astra` | `high` | `read-only`, set in the file | Second opinion on a sibling leaf's diff from a fresh session. The role file enforces read-only, so the critic cannot patch what it reviews. |
| `grunt` | `gpt-5.6-luna` | `xhigh` | inherited | Mechanical refactors, fixtures, search, small tests. Raise to `max` when a mechanical task fails verification; `luna` stops there. |

The role file carries the model and effort, so a lead brief can name roles
instead of models: "spawn a `feature` agent for the parser rewrite, a `grunt`
agent for the fixture updates, then a `critic` on the parser diff". Leave the
decomposition to the lead when the split is not obvious from outside.

Take the model and effort from `preferences.md` or the user's request; omit both
flags to use the CLI's configured default.

```bash
codex exec --json -s workspace-write \
  -c approval_policy=never \
  -m gpt-6-astra -c model_reasoning_effort=medium \
  -c agents.max_concurrent_threads_per_session=<cap> \
  -c 'sandbox_workspace_write.writable_roots=["<worktree>/.git"]' \
  --output-schema docs/campaign-hq/schemas/worker-result.json \
  -C <worktree> \
  -o docs/campaign-hq/out/<task>.json \
  - < docs/campaign-hq/briefs/<task>.md
```

`agents.max_concurrent_threads_per_session` caps open subagent threads.
`agents.default_subagent_model` and `agents.default_subagent_reasoning_effort`
set fallbacks; an explicit spawn choice or a role file wins over both. Leaves
inherit the lead's sandbox policy unless their role sets `sandbox_mode`, so a
`workspace-write` lead gives its leaves write access to the same workspace.

The `--json` stream shows only the lead's wait calls. Each leaf writes its own
rollout file under `~/.codex/sessions/`, whose `turn_context` records carry the
model and effort it ran with. Read those to confirm a leaf's role took effect;
a lead's self-report about its own effort is not reliable.

No config key limits nesting depth. The two-level depth cap is a brief-level
rule, and every lead brief must forbid its leaves from spawning further agents.
Keep leaves off `ultra` for the same reason: that tier delegates on its own.

## Capabilities

| Capability | Invocation | Campaign use |
|---|---|---|
| Structured final report | `--output-schema docs/campaign-hq/schemas/worker-result.json` | machine-checkable collection |
| Live web search | `-c web_search=live` (default is `cached`, an index with no live fetch; `codex exec` has no `--search` flag) | volatile facts, current APIs, advisories, versions |
| Image input | `-i current.png -i target.png` | UI bug reproduction from screenshots and mocks |
| Image generation | prompt the built-in `image_gen` tool | asset generation; the tool saves under `~/.codex/generated_images/<session>/`, so the brief must require copying the file into the repo and verifying it exists |
| Review mode | `codex exec review --base <ref> -m gpt-6-astra -c model_reasoning_effort=high` | read-only review gate in the consultant shape |
| Session continuation | `codex exec resume <session-id> "<correction>"` | incremental steering after a finished run |
| Native subagents | prompt the built-in multi-agent tools (`spawn_agent`, `wait_agent`, `send_input`, `close_agent`); role files in `.codex/agents/` set each leaf's model and effort; leaves without a role inherit the lead's | a codex worker fans out its own parallel subagents inside one workspace; see Lead And Leaf Roles above and the squads reference |

## Steering And Retry

Capture each worker's session id from the `--json` event stream and record it in
the fleet table. Resume when the result is mostly right and needs a correction:

```bash
codex exec resume <session-id> "<correction>"
```

Redispatch from a clean brief when the approach is wrong. Use `codex fork
<session-id>` only when exploring an alternative from the same context is more
valuable than a clean retry.

## Collection

Treat the worker's report as a claim. Inspect the commit, rerun the verification
command, and record the result in `CAMPAIGN.md` and `LEARNINGS.md`.
