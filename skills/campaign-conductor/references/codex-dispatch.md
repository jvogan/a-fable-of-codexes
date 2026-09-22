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
codex exec -s read-only -m gpt-6-sol "Reply with the single word ok"
codex exec -s read-only -m gpt-6-luna "Reply with the single word ok"
```

Record the result in `preferences.md`. The smoke tests confirm the account can
reach the worker and leaf models; GPT-6 rollouts are staged by plan, and
Enterprise workspaces need an admin to enable them. If a model is rejected,
auth fails, or limits are exhausted, route that work to Claude workers until
the user changes the setup, and record the change.

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
- Fan-out policy: run alone, or spawn at most five named leaves that must not spawn further agents

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

Three independent controls set a worker's cost and quality: the model, the
reasoning effort (`low`, `medium`, `high`, `xhigh`, `max`, `ultra`), and the
optional `fast` service tier, which runs about twice as fast for more usage.
Codex lists three GPT-6 models:

- `gpt-6-sol`: the campaign worker and the judgment leaves. Default effort in
  this skill is `high`.
- `gpt-6-luna`: the mechanical leaf and scout model, at `max`. Efforts stop
  at `max`.
- `gpt-6-astra`: the most capable model, outside the default fleet. It runs at
  `max`, read-only, only when the user explicitly asks for an exceptional
  effort on a rare, very hard question.

`ultra` is `max` plus automatic delegation, so a worker on `ultra` spawns its
own subagents. No default shape uses it; run it only on an explicit request,
never for a leaf, a consultant, or the Astra run.

Every shape the conductor or an Opus squad lead calls directly:

| Shape | Model | Effort | Sandbox | Use |
|---|---|---|---|---|
| Worker | `gpt-6-sol` | `high` | `workspace-write` | the default; runs alone or fans out to at most five leaves |
| Consultant | `gpt-6-sol` | `high` | `read-only` | architecture answers, review of a Claude worker's diff |
| Arbiter | `gpt-6-sol` | `xhigh` | `read-only` | bake-off judging, final arbitration between a critic and an author |
| Scout | `gpt-6-luna` | `max` | `read-only`, `-c web_search=live` for research | surveys, current APIs, advisories |
| Deep consult | `gpt-6-astra` | `max` | `read-only` | explicit user request only; one very hard question |

Raise a Sol worker to `xhigh` for a task that already failed at `high` or for
thorny debugging, and record the change in the fleet table. A cheap model on
genuinely hard work produces rework, so give Luna only mechanical work.

Above 272K input tokens the API adds a long-context premium. The CLI compacts
near that point unless `auto_compact_token_limit` is raised, so raise it only
for a task that needs a larger window.

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

## Sol Worker And Leaves

Subagents inherit the parent's model, reasoning effort, and sandbox policy
unless a role sets them. A role is a standalone TOML file under `.codex/agents/`
(project-scoped) or `~/.codex/agents/` (personal). Each file defines `name`,
`description`, and `developer_instructions`, and may set `model`,
`model_reasoning_effort`, and `sandbox_mode`. Built-in roles are `default`,
`worker`, and `explorer`.

- <https://learn.chatgpt.com/docs/config-file/config-reference>
- <https://learn.chatgpt.com/docs/agent-configuration/subagents>

Bootstrap copies three roles from the skill's `assets/codex-agents/`, and
a campaign can edit them, add roles, or ignore them. Roles are named for the
job, so the next model generation changes one line per file:

```toml
# .codex/agents/grunt.toml
name = "grunt"
description = "Mechanical leaf: refactors, fixtures, search, small tests, and routine edits."
developer_instructions = "Own only the files named in your task. Run the verification command before reporting. Do not spawn agents."
model = "gpt-6-luna"
model_reasoning_effort = "max"
```

| Role | Model | Effort | Sandbox | Leaf work |
|---|---|---|---|---|
| `feature` | `gpt-6-sol` | `high` | inherited | A bounded sub-feature, bug fix, or test suite that needs design care. |
| `critic` | `gpt-6-sol` | `medium` | `read-only`, set in the file | Second opinion on a sibling leaf's diff from a fresh session; it cannot patch what it reviews. |
| `grunt` | `gpt-6-luna` | `max` | inherited | Mechanical refactors, fixtures, search, small tests. Move a task that fails verification twice to `feature`. |

A Sol brief can name roles instead of models: "spawn a `feature` leaf for the
parser rewrite, a `grunt` leaf for the fixture updates, then a `critic` on the
parser diff". Leave the decomposition to the Sol worker when the split is not
obvious from outside.

Cap the team at five concurrent leaves:

```bash
codex exec --json -s workspace-write \
  -c approval_policy=never \
  -m gpt-6-sol -c model_reasoning_effort=high \
  -c agents.max_concurrent_threads_per_session=5 \
  -c 'sandbox_workspace_write.writable_roots=["<worktree>/.git"]' \
  --output-schema docs/campaign-hq/schemas/worker-result.json \
  -C <worktree> \
  -o docs/campaign-hq/out/<task>.json \
  - < docs/campaign-hq/briefs/<task>.md
```

`agents.max_concurrent_threads_per_session` caps open subagent threads.
`agents.default_subagent_model` and `agents.default_subagent_reasoning_effort`
set fallbacks; an explicit spawn choice or a role file wins over both. Leaves
inherit the Sol worker's sandbox policy unless their role sets `sandbox_mode`,
so a `workspace-write` worker gives its leaves write access to the same
workspace. The brief must assign each leaf disjoint files.

The `--json` stream shows only the worker's wait calls. Each leaf writes its own
rollout file under `~/.codex/sessions/`, whose `turn_context` records carry the
model and effort it ran with. Read those to confirm a leaf's role took effect;
a worker's self-report about its leaves is not reliable.

No config key limits nesting depth. Every Sol brief must forbid its leaves
from spawning further agents, and leaves stay off `ultra` because that tier
delegates on its own.

## Capabilities

| Capability | Invocation | Campaign use |
|---|---|---|
| Structured final report | `--output-schema docs/campaign-hq/schemas/worker-result.json` | machine-checkable collection |
| Live web search | `-c web_search=live` (default is `cached`, an index with no live fetch; `codex exec` has no `--search` flag) | volatile facts, current APIs, advisories, versions |
| Image input | `-i current.png -i target.png` | UI bug reproduction from screenshots and mocks |
| Image generation | prompt the built-in `image_gen` tool | asset generation; the tool saves under `~/.codex/generated_images/<session>/`, so the brief must require copying the file into the repo and verifying it exists |
| Review mode | `codex exec review --base <ref> -m gpt-6-sol -c model_reasoning_effort=high` | read-only review gate in the consultant shape |
| Session continuation | `codex exec resume <session-id> "<correction>"` | incremental steering after a finished run |
| Native subagents | prompt the built-in multi-agent tools (`spawn_agent`, `wait_agent`, `send_input`, `close_agent`); role files in `.codex/agents/` set each leaf's model and effort; leaves without a role inherit the worker's | a Sol worker fans out up to five leaves inside one workspace; see Sol Worker And Leaves above |

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
