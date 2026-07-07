# Codex Dispatch

Read this before dispatching Codex CLI workers.

## Cost And Auth Policy

Codex can be authenticated through a ChatGPT plan or an API key. ChatGPT-plan
auth consumes plan usage and plan limits vary. API-key auth is token-priced.
Do not promise unlimited or flat-rate worker capacity. Size waves to the user's
available plan, credits, and tolerance for spend.

Useful public docs:

- <https://help.openai.com/en/articles/11369540-using-codex-with-your-chatgpt-plan>
- <https://developers.openai.com/codex/pricing>
- <https://github.com/openai/codex>

## Preflight

Run once at campaign kickoff:

```bash
codex --version
codex login status
```

Record the result in `preferences.md`. If auth fails or limits are exhausted,
route implementation work to Claude workers until the user changes the setup.

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

Use `read-only` for scouts and reviewers. Use `workspace-write` for writers.
Keep network on only when the task needs dependency installation, package docs,
or live research.

Never dispatch with `approval_policy=never`: it removes the approval gate
entirely, and host permission systems (including Claude Code's classifier)
rightly deny it for unattended runs. Use `on-request` with the auto reviewer
instead — escalations get reviewed by a model gate rather than waved through.
The values contain hyphens/underscores, so quote them as TOML strings:
`-c 'approval_policy="on-request"' -c 'approvals_reviewer="auto_review"'`.

One writer:

```bash
codex exec --json -s workspace-write \
  -c 'approval_policy="on-request"' \
  -c 'approvals_reviewer="auto_review"' \
  -c sandbox_workspace_write.network_access=true \
  --output-schema docs/campaign-hq/schemas/worker-result.json \
  -C <worktree> \
  -o docs/campaign-hq/out/<task>.json \
  - < docs/campaign-hq/briefs/<task>.md
```

Read-only scout with live web search:

```bash
codex exec --json --search -s read-only \
  -c 'approval_policy="on-request"' \
  -c 'approvals_reviewer="auto_review"' \
  -C <repo> \
  -o docs/campaign-hq/out/<task>.json \
  - < docs/campaign-hq/briefs/<task>.md
```

Second Codex home, when the user has configured one:

```bash
CODEX_HOME="$HOME/.codex-account2" codex exec --json -s workspace-write \
  -c 'approval_policy="on-request"' \
  -c 'approvals_reviewer="auto_review"' \
  -c sandbox_workspace_write.network_access=true \
  --output-schema docs/campaign-hq/schemas/worker-result.json \
  -C <worktree> \
  -o docs/campaign-hq/out/<task>.json \
  - < docs/campaign-hq/briefs/<task>.md
```

Omit `--skip-git-repo-check` for normal campaign worktrees. A bad `-C` should
fail quickly instead of running outside the intended repo.

## Model And Effort

Default every worker to the strongest model and reasoning the user's config
provides; a cheap model on a real task produces rework, and architecture,
debugging, and judging always run at highest effort. A live user request for a
specific model or reasoning level wins. Do not silently "upgrade" or
"downgrade" that request to the default policy.

Prefer per-call flags such as `-m <model> -c model_reasoning_effort=<level>`
when a single task needs a different policy; do not rewrite the user's global
config unless asked. If a requested model or effort value is unavailable, stop
and record the limitation instead of pretending the requested policy was used.

Avoid hard-coded model names in briefs unless they come from `preferences.md` or
the user just specified them. When the user specifies a model or effort policy,
write it into the brief and the fleet table.

## Capabilities

| Capability | Invocation | Campaign use |
|---|---|---|
| Structured final report | `--output-schema docs/campaign-hq/schemas/worker-result.json` | machine-checkable collection |
| Live web search | `--search` | volatile facts, current APIs, advisories, versions |
| Image input | `-i current.png -i target.png` | UI bug reproduction from screenshots and mocks |
| Image generation | prompt the built-in `image_gen` tool | asset generation; the tool saves under `~/.codex/generated_images/<session>/`, so the brief must require copying the file into the repo and verifying it exists |
| Review mode | `codex exec review --base <ref>` | read-only review gate |
| Session continuation | `codex exec resume <session-id> "<correction>"` | incremental steering after a finished run |
| Native subagents | prompt the built-in `multi_agent_v1` tools (`spawn_agent`, `wait_agent`, `send_input`, `close_agent`) | a codex worker fans out its own parallel subagents inside one workspace; see the squads reference |

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
