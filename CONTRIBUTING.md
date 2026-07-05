# Contributing

Skills live at `skills/<name>/SKILL.md` per the
[Agent Skills spec](https://agentskills.io/specification).

- Run `python3 scripts/validate.py` and `npx --yes skills add . --list`
  before committing; CI runs both on every push and pull request.
- Follow the working rules and writing style in [CLAUDE.md](CLAUDE.md) —
  they apply to human and agent contributors alike.
- Keep each SKILL.md body under 500 lines. Tighten existing text before
  appending new text.
- Update `examples/` when a skill's file formats change.
- New skills need a README entry describing what they add.
