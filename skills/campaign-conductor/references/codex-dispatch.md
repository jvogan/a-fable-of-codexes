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
codex exec -s read-only -m gpt-6.2-sol "Reply with the single word ok"
codex exec -s read-only -m gpt-6.1-terra "Reply with the single word ok"
```

Record the result in `preferences.md`. The smoke tests confirm the account can
reach the worker and leaf models; model rollouts are staged by plan, and
Enterprise workspaces need an admin to enable them. If a model is rejected,
auth fails, or limits are exhausted, route that work to Claude workers until
the user changes the setup, and record the change.

Run the smoke tests from the project root. Codex reads project-local
configuration, including the `.codex/agents/` role files, only in a trusted
project, and a linked worktree takes its main checkout's trust. If a smoke test
prints `Untrusted project-local configuration is disabled`, a worker cannot
spawn leaves by role and reports itself blocked. Trusting a parent folder does
not cover a repository inside it, and a `-c` override does not grant trust.
Trust also lets the project's MCP servers run commands outside the sandbox, so
ask the user before granting it: they accept the trust prompt in an
interactive `codex` session in the project root, or approve adding `--trust`
to one smoke test. Trust persists; record it in the permission envelope.

## Worker Brief Contract

Every Codex brief must include:

- Goal and success criteria
- Branch, worktree path, and base commit
- Files/directories owned by this worker
- Files/directories excluded because siblings own them
- Repo conventions to preserve
- Verification command to run from the worktree root
- Instruction to leave changes uncommitted and report every changed path
- Required final report schema
- Fan-out policy: run alone, or spawn named leaves that must not spawn further
  agents, one leaf per disjoint file group

Codex workers take no input mid-run, so the initial brief must be complete
enough to run without follow-up questions.

## Standard Dispatch

Use `read-only` for scouts, reviewers, and consultations. Use `workspace-write`
for writers. Keep network on only when the task needs dependency installation,
package docs, or live research. `workspace-write` keeps git metadata read-only,
and in a linked worktree `writable_roots` does not lift that (checked on
codex-cli 0.169.0), so a Codex worker cannot run `git add` or `git commit`.
The brief tells the worker to leave its changes uncommitted, and the collector
commits them (see Collection).

`approval_policy=never` keeps the envelope fixed: anything the sandbox blocks
fails instead of asking. If a host blocks `never` for unattended runs,
`--approve-for-me` routes escalation requests through Codex's automatic
reviewer. Record that choice in `preferences.md`, since it lets a model widen
the envelope mid-run.

Run every dispatch as a background command and read the `-o` report when it
exits. The events file holds the `--json` stream: every command the worker ran
and its output. Read only its first line, the `thread.started` event, whose
`thread_id` is the session id. When a worker fails or stalls, send a Haiku
agent to find the failing command in the rest.

One writer:

```bash
codex exec --json -s workspace-write \
  -m gpt-6.2-sol -c model_reasoning_effort=high \
  -c approval_policy=never \
  -c sandbox_workspace_write.network_access=true \
  --output-schema docs/campaign-hq/schemas/worker-result.json \
  -C <worktree> \
  -o docs/campaign-hq/out/<task>.json \
  - < docs/campaign-hq/briefs/<task>.md \
  > docs/campaign-hq/out/<task>.events.jsonl
```

Read-only scout with live web search:

```bash
codex exec --json -s read-only \
  -m gpt-6.1-terra -c model_reasoning_effort=max \
  -c approval_policy=never \
  -c web_search=live \
  --output-schema docs/campaign-hq/schemas/scout-result.json \
  -C <repo> \
  -o docs/campaign-hq/out/<task>.json \
  - < docs/campaign-hq/briefs/<task>.md \
  > docs/campaign-hq/out/<task>.events.jsonl
```

A sweep launches that command once per package, file group, or question, all
in the background at once, with `-c model_reasoning_effort=xhigh`.

`codex exec` enables web search by default, but in `cached` mode (an
OpenAI-maintained index, no live fetch), so a scout needing the live web must
set `web_search=live`. Values are `live`, `indexed`, `cached`, and `disabled`;
set it per call with `-c web_search=<mode>` or as a top-level config key.
`codex exec` has no `--search` flag; the interactive `codex` command has one.
Check `codex exec --help` for the version in use.

To dispatch through a second Codex home that the user has configured, prefix
the command with `CODEX_HOME="<second-codex-home>"` and note the home in the
fleet table.

Omit `--skip-git-repo-check` for normal campaign worktrees. A bad `-C` should
fail quickly instead of running outside the intended repo.

## Model And Effort

Three independent controls set a worker's cost and quality: the model, the
reasoning effort (`low`, `medium`, `high`, `xhigh`, `max`, `ultra`), and the
optional `fast` service tier, which runs about twice as fast for more usage.
The fleet uses three Codex models:

- `gpt-6.2-sol`: the campaign worker and the judgment leaves, at `high` in this
  skill.
- `gpt-6.1-terra`: the mechanical leaf and scout model. It runs at `xhigh`
  wherever many run at once (the `grunt` role, parallel sweeps) and at `max`
  for a single deep scout.
- `gpt-6.2-astra`: the most capable model, outside the default fleet. At API
  rates it costs four times Sol per token, and OpenAI reports Sol nearly
  matching it on merge-ready code changes at about a fifth of the cost per
  task. It runs at `max`, read-only, only when the user explicitly asks for an
  exceptional effort on a rare, very hard question.

With no effort flag or config value, all three run at `low`.

`ultra` is `max` plus automatic delegation, so a worker on `ultra` spawns its
own subagents. No default shape uses it; run it only on an explicit request,
never for a leaf, a consultant, or the Astra run.

Every shape the conductor or an Opus squad lead calls directly:

| Shape | Model | Effort | Sandbox | Use |
|---|---|---|---|---|
| Worker | `gpt-6.2-sol` | `high` | `workspace-write` | the default; runs alone or fans out a leaf team, one leaf per disjoint file group |
| Consultant | `gpt-6.2-sol` | `high` | `read-only` | architecture answers, review of a Claude worker's diff |
| Arbiter | `gpt-6.2-sol` | `xhigh` | `read-only` | bake-off judging, final arbitration between a critic and an author |
| Scout | `gpt-6.1-terra` | `max` | `read-only`, `-c web_search=live` for research | one deep survey, current APIs, advisories |
| Sweep scout | `gpt-6.1-terra` | `xhigh` | `read-only` | many in parallel, one per package, file group, or question |
| Deep consult | `gpt-6.2-astra` | `max` | `read-only` | explicit user request only; one very hard question |

No shape or role runs below `high`. Raise a Sol worker to `xhigh` for a task
that already failed at `high` or for thorny debugging, and record the change in
the fleet table. A cheaper model on hard work produces rework, so give Terra
mechanical work and read-only sweeps.

Codex gives `gpt-6.2-sol` and `gpt-6.1-terra` a 500K-token default context
window and `gpt-6.2-astra` 272K, and compacts a session as it nears that limit.
`model_context_window` raises the limit; raise it only for a task that needs
more, since every turn resends the context. With API-key auth, earlier Sol
models billed a request above 272K input tokens at long-context rates for the
whole request, and a 500K window lets a session cross that line without any
config change.

Precedence is the user's live request, then `preferences.md`, then the skill
defaults, bounded by what the active CLI and account support. A live request
for a specific model or effort wins; do not silently "upgrade" or "downgrade"
it. Pass `-m <model> -c model_reasoning_effort=<level>` on every dispatch, as
the dispatch commands in this file do: the user's config default may name
another model or effort. Do not rewrite the user's global config unless asked.
If a requested model or effort is unavailable, say so before dispatching, as
Worker Routing in SKILL.md directs, and record the limitation.

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

Bootstrap copies three roles from the skill's `assets/codex-agents/`, and a
campaign can edit them, add roles, or ignore them. Codex loads them only in a
trusted project (see Preflight). Roles are named for the job, so the next model
generation needs a one-line edit per file:

```toml
# .codex/agents/grunt.toml
name = "grunt"
description = "Mechanical leaf: refactors, fixtures, search, small tests, and routine edits."
developer_instructions = "Own only the files named in your task. Run the verification command before reporting. Do not spawn agents."
model = "gpt-6.1-terra"
model_reasoning_effort = "xhigh"
```

| Role | Model | Effort | Sandbox | Leaf work |
|---|---|---|---|---|
| `feature` | `gpt-6.2-sol` | `high` | inherited | A bounded sub-feature, bug fix, or test suite that needs design care. |
| `critic` | `gpt-6.2-sol` | `high` | `read-only`, set in the file | Second opinion on a sibling leaf's diff from a fresh session; it cannot patch what it reviews. |
| `grunt` | `gpt-6.1-terra` | `xhigh` | inherited | Mechanical refactors, fixtures, search, small tests. Move a task that fails verification twice to `feature`. |

A Sol brief can name roles instead of models: "spawn a `feature` leaf for the
parser rewrite, a `grunt` leaf for the fixture updates, then a `critic` on the
parser diff". Leave the decomposition to the Sol worker when the split is not
obvious from outside.

Set the thread limit to the team the brief plans, so Codex's configured
default does not throttle a wide team:

```bash
codex exec --json -s workspace-write \
  -c approval_policy=never \
  -m gpt-6.2-sol -c model_reasoning_effort=high \
  -c agents.max_concurrent_threads_per_session=<team-size> \
  --output-schema docs/campaign-hq/schemas/worker-result.json \
  -C <worktree> \
  -o docs/campaign-hq/out/<task>.json \
  - < docs/campaign-hq/briefs/<task>.md \
  > docs/campaign-hq/out/<task>.events.jsonl
```

`agents.max_concurrent_threads_per_session` sets how many subagent threads run
at once. Size the team to the task: one leaf per disjoint file group, bounded
only by the account's rate limits. An explicit spawn choice
or a role file wins over the fallbacks that `agents.default_subagent_model`
and `agents.default_subagent_reasoning_effort` set. Leaves inherit the Sol
worker's sandbox policy unless their role sets `sandbox_mode`, so a
`workspace-write` worker gives its leaves write access to the same workspace.
The brief must assign each leaf disjoint files.

The `--json` stream shows only the worker's wait calls. Each leaf writes its
own rollout file under `~/.codex/sessions/`; the file's `turn_context` records
carry the model and effort the leaf ran with. Read those records to confirm a
leaf's role took effect; a worker's self-report about its leaves is unreliable.

`agents.max_depth` applies only to multi-agent V1, and V2 ignores it, so every
Sol brief must forbid its leaves from spawning further agents.

## Capabilities

| Capability | Invocation | Campaign use |
|---|---|---|
| Structured final report | `--output-schema docs/campaign-hq/schemas/worker-result.json` for writers, `scout-result.json` for scouts | machine-checkable collection |
| Live web search | `-c web_search=live` (default is `cached`, an index with no live fetch; `codex exec` has no `--search` flag) | volatile facts, current APIs, advisories, versions |
| Image input | `-i current.png -i target.png` | UI bug reproduction from screenshots and mocks |
| Image generation | prompt the built-in `image_gen` tool | asset generation; the tool saves under `~/.codex/generated_images/<session>/`, so the brief must require copying the file into the repo and verifying it exists |
| Review mode | `codex exec review --base <ref> -m gpt-6.2-sol -c model_reasoning_effort=high` | read-only review gate in the consultant shape |
| Session continuation | `codex exec resume <session-id> "<correction>"` | incremental steering after a finished run |
| Native subagents | prompt the built-in multi-agent tools (`spawn_agent`, `wait_agent`, `send_input`, `close_agent`); role files in `.codex/agents/` set each leaf's model and effort; leaves without a role inherit the worker's | a Sol worker fans out a leaf team inside one workspace; see Sol Worker And Leaves above |

## Steering And Retry

Record each worker's session id in the fleet table. Resume when the result is
mostly right and needs a correction:

```bash
codex exec resume <session-id> "<correction>"
```

Redispatch from a clean brief when the approach is wrong. Use `codex fork
<session-id>` only when exploring an alternative from the same context is more
valuable than a clean retry.

## Collection

Commit the worker's changes first, staging only the paths in its report:

```bash
git -C <worktree> add -- <files_changed>
git -C <worktree> commit -m "campaign/<task>: <summary>"
git -C <worktree> status --short
```

A path the last command still lists is output the worker did not report:
inspect it before review. Then treat the report as a claim. An agent that did
not write the change inspects the commit and reruns the verification command:
the conductor for high-risk work, an integration or verifier worker otherwise.
Record the result in `CAMPAIGN.md` and `LEARNINGS.md`.
