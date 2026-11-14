#!/usr/bin/env python3
"""Validate skills against the Agent Skills spec (agentskills.io/specification)
plus this repo's own limits. Standard library only."""
import json
import re
import sys
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:
    tomllib = None

ROOT = Path(__file__).resolve().parent.parent
MAX_BODY_LINES = 500
ROLE_KEYS = ("name", "description", "developer_instructions", "model", "model_reasoning_effort")
EFFORTS = {"low", "medium", "high", "xhigh", "max", "ultra"}
errors = []


def err(path, msg):
    errors.append(f"{path}: {msg}")


def parse_frontmatter(path, text):
    """Parse the small YAML subset allowed for skill frontmatter."""
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
    if not m:
        err(path, "missing YAML frontmatter")
        return None, None

    fm, body = m.groups()
    lines = fm.splitlines()
    data = {}
    i = 0

    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1
            continue
        top = re.fullmatch(r"([A-Za-z][A-Za-z0-9_-]*):(.*)", line)
        if not top or line.startswith((" ", "\t")):
            err(path, f"invalid frontmatter line {i + 1}: {line!r}")
            return None, body

        key, raw_value = top.group(1), top.group(2)
        if key in data:
            err(path, f"duplicate frontmatter field: {key}")
            return None, body
        if raw_value and not raw_value.startswith(" "):
            err(path, f"missing space after colon for field: {key}")
            return None, body

        value = raw_value[1:] if raw_value.startswith(" ") else ""
        if value in {">", ">-", "|", "|-"}:
            block = []
            i += 1
            while i < len(lines) and (lines[i].startswith("  ") or not lines[i].strip()):
                block.append(lines[i][2:] if lines[i].startswith("  ") else "")
                i += 1
            data[key] = " ".join(part.strip() for part in block if part.strip()) if value.startswith(">") else "\n".join(block)
            continue

        if value == "":
            children = {}
            i += 1
            while i < len(lines) and lines[i].startswith("  "):
                child = re.fullmatch(r"  ([A-Za-z][A-Za-z0-9_-]*): (.*)", lines[i])
                if not child:
                    err(path, f"invalid nested frontmatter line {i + 1}: {lines[i]!r}")
                    return None, body
                child_key, child_value = child.groups()
                if ": " in child_value and not child_value.startswith(('"', "'")):
                    err(path, f"invalid YAML plain scalar in {key}.{child_key}; quote it or use a block scalar")
                    return None, body
                children[child_key] = child_value.strip('"\'')
                i += 1
            data[key] = children
            continue

        if ": " in value and not value.startswith(('"', "'")):
            err(path, f"invalid YAML plain scalar in {key}; quote it or use a block scalar")
            return None, body
        data[key] = value.strip('"\'')
        i += 1

    return data, body


def check_role_files(d):
    """Codex role files: bootstrap copies these into .codex/agents/, and a
    missing key silently falls back to the parent worker's model."""
    role_files = sorted((d / "assets" / "codex-agents").glob("*.toml"))
    if role_files and tomllib is None:
        err(d, "Python 3.11+ required to validate Codex role files")
        role_files = []
    for role in role_files:
        try:
            data = tomllib.loads(role.read_text())
        except tomllib.TOMLDecodeError as e:
            err(role, f"invalid TOML: {e}")
            continue
        for key in ROLE_KEYS:
            if not data.get(key):
                err(role, f"missing required key: {key}")
        if data.get("name") and data["name"] != role.stem:
            err(role, f"name {data['name']!r} does not match file name {role.stem!r}")
        effort = data.get("model_reasoning_effort")
        if effort and effort not in EFFORTS:
            err(role, f"unknown model_reasoning_effort {effort!r}")


def check_schemas(d):
    """Report schemas: Codex sends --output-schema in strict mode and rejects
    the request when any object leaves additionalProperties unset."""
    for schema in sorted((d / "assets").glob("**/schemas/*.json")):
        try:
            data = json.loads(schema.read_text())
        except json.JSONDecodeError as e:
            err(schema, f"invalid JSON: {e}")
            continue
        stack = [("$", data)]
        while stack:
            where, node = stack.pop()
            if isinstance(node, dict):
                if node.get("type") == "object" and node.get("additionalProperties") is not False:
                    err(schema, f"{where}: object must set additionalProperties to false")
                stack.extend((f"{where}.{k}", v) for k, v in node.items())
            elif isinstance(node, list):
                stack.extend((f"{where}[{i}]", v) for i, v in enumerate(node))


skill_dirs = sorted(p for p in (ROOT / "skills").iterdir() if p.is_dir())
if not skill_dirs:
    err("skills/", "no skill directories found")

for d in skill_dirs:
    # Asset checks run first so a frontmatter error does not hide them.
    check_role_files(d)
    check_schemas(d)
    md = d / "SKILL.md"
    if not md.exists():
        err(d, "missing SKILL.md")
        continue
    text = md.read_text()
    fields, body = parse_frontmatter(md, text)
    if fields is None:
        continue

    name = fields.get("name")
    if not name:
        err(md, "missing required field: name")
    else:
        if len(name) > 64 or not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", name):
            err(md, f"invalid name {name!r} (1-64 chars, lowercase alphanumerics, single hyphens)")
        if name != d.name:
            err(md, f"name {name!r} does not match directory {d.name!r}")

    desc = fields.get("description")
    if not desc:
        err(md, "missing required field: description")
    elif len(desc) > 1024:
        err(md, f"description is {len(desc)} chars; spec maximum is 1024")

    compat = fields.get("compatibility")
    if compat and len(compat) > 500:
        err(md, f"compatibility is {len(compat)} chars; spec maximum is 500")

    body_lines = len(body.splitlines())
    if body_lines >= MAX_BODY_LINES:
        err(md, f"body is {body_lines} lines; keep under {MAX_BODY_LINES}")

    for ref in re.findall(r"\]\((?!https?://|#|mailto:)([^)\s]+?)(?:#[^)]*)?\)", body):
        if not (d / ref).exists():
            err(md, f"broken relative link: {ref}")

if errors:
    print("\n".join(errors))
    sys.exit(1)
print(f"OK: {len(skill_dirs)} skill(s) valid")
