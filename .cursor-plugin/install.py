#!/usr/bin/env python3
"""
Sextant Cursor Plugin Installer
Resolves ! include directives from skills/ and installs Cursor rules and commands.

Usage:
  python .cursor-plugin/install.py             # install into .cursor/ in current directory
  python .cursor-plugin/install.py --global    # install into ~/.cursor/ (all Cursor projects)
  python .cursor-plugin/install.py --uninstall # remove Sextant files from target directory
"""

import sys
import re
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.resolve()
REPO_ROOT = SCRIPT_DIR.parent
SKILLS_DIR = REPO_ROOT / "skills"

# ── Skill definitions ─────────────────────────────────────────────────────────

RULES = [
    {
        "source": SKILLS_DIR / "principles" / "SKILL_BODY.md",
        "output_name": "sextant-principles.mdc",
        "frontmatter": {
            "description": "Sextant engineering principles — always-active quality baselines (§0–§6). Applied to every coding task.",
            "alwaysApply": True,
        },
    },
    {
        "source": SKILLS_DIR / "tool-gitnexus" / "SKILL_BODY.md",
        "output_name": "sextant-gitnexus.mdc",
        "frontmatter": {
            "description": "GitNexus MCP tool reference for Sextant workflows (context, impact, query, trace, diff_review, rename).",
            "alwaysApply": False,
            "globs": [".gitnexus/**"],
        },
    },
]

COMMANDS = [
    ("principles",          "sextant"),
    ("fix-bug",             "sextant-fix-bug"),
    ("add-feature",         "sextant-add-feature"),
    ("modify-feature",      "sextant-modify-feature"),
    ("debug",               "sextant-debug"),
    ("plan",                "sextant-plan"),
    ("ship",                "sextant-ship"),
    ("migrate",             "sextant-migrate"),
    ("review-code",         "sextant-review-code"),
    ("write-tests",         "sextant-write-tests"),
    ("refine-requirements", "sextant-refine-requirements"),
    ("security",            "sextant-security"),
]

# ── Core utilities ────────────────────────────────────────────────────────────

def strip_frontmatter(text: str) -> str:
    """Return text with leading YAML frontmatter removed.

    Only strips if the file actually starts with '---' (i.e. has YAML
    frontmatter).  Files that start with regular Markdown content — like
    SKILL_BODY.md files — are returned unchanged, even if they contain
    '---' horizontal-rule separators inside the body.
    """
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].strip() != "---":
        return text  # no frontmatter; return full content as-is
    count = 0
    for i, line in enumerate(lines):
        if line.strip() == "---":
            count += 1
            if count == 2:
                return "".join(lines[i + 1:])
    return ""  # no closing --- found; matches awk behavior


def extract_frontmatter_text(text: str) -> str:
    """Return the raw YAML text between the first pair of --- delimiters."""
    lines = text.splitlines(keepends=True)
    collecting = False
    result = []
    for line in lines:
        if line.strip() == "---":
            if not collecting:
                collecting = True
                continue
            else:
                break
        if collecting:
            result.append(line)
    return "".join(result)


def extract_description(text: str) -> str:
    """Extract the description field from YAML frontmatter.

    Handles both plain scalar and >- block scalar formats without
    requiring an external yaml library.
    """
    fm_text = extract_frontmatter_text(text)
    lines = fm_text.splitlines()
    result_lines = []
    in_description = False

    for line in lines:
        if re.match(r"^description\s*:\s*>\-\s*$", line):
            in_description = True
            continue
        if re.match(r"^description\s*:\s*(.+)$", line) and not in_description:
            m = re.match(r"^description\s*:\s*(.+)$", line)
            return m.group(1).strip().strip("'\"")
        if in_description:
            if line.startswith("  ") or line.startswith("\t"):
                result_lines.append(line.strip())
            else:
                break  # end of block scalar

    return " ".join(result_lines).strip()


def resolve_includes(text, base_dir, skip_paths=None):
    """Recursively inline all ! include directives, stripping frontmatter from inclusions.

    skip_paths: if provided, any ! include whose resolved absolute path is in
    this set is silently dropped rather than inlined.  Used by build_command()
    to avoid re-embedding content that is already deployed as a Cursor rule.
    """
    lines = text.splitlines(keepends=True)
    result = []
    for line in lines:
        m = re.match(r"^!(.+)$", line.rstrip())
        if m:
            include_rel = m.group(1).strip()
            include_path = (base_dir / include_rel).resolve()
            if skip_paths and include_path in skip_paths:
                continue  # already covered by an always-on rule; skip
            try:
                included_text = include_path.read_text(encoding="utf-8")
            except FileNotFoundError:
                print(f"Warning: include not found: {include_path}", file=sys.stderr)
                continue
            included_body = strip_frontmatter(included_text)
            resolved = resolve_includes(included_body, include_path.parent, skip_paths)
            result.append(resolved)
        else:
            result.append(line)
    return "".join(result)


# ── Content generators ────────────────────────────────────────────────────────

def render_mdc_frontmatter(fm: dict) -> str:
    """Render MDC YAML frontmatter block."""
    lines = ["---\n"]
    lines.append(f"description: {fm['description']!r}\n")
    lines.append(f"alwaysApply: {str(fm['alwaysApply']).lower()}\n")
    if "globs" in fm:
        lines.append("globs:\n")
        for g in fm["globs"]:
            lines.append(f"  - {g!r}\n")
    lines.append("---\n")
    return "".join(lines)


def build_rule(rule_def: dict) -> str:
    """Build .mdc rule content from a SKILL_BODY.md source."""
    source_path: Path = rule_def["source"]
    body = source_path.read_text(encoding="utf-8")
    body = resolve_includes(body, source_path.parent)
    return render_mdc_frontmatter(rule_def["frontmatter"]) + "\n" + body


def build_command(skill_dir_name: str) -> str:
    """Build .md command content from a skill's SKILL.md source."""
    skill_dir = SKILLS_DIR / skill_dir_name
    source_path = skill_dir / "SKILL.md"
    source_text = source_path.read_text(encoding="utf-8")

    description = extract_description(source_text)
    body = strip_frontmatter(source_text)
    # The principles fallback skill IS the shared principles content — don't
    # skip its own include, or the command body would be empty.
    skip = None if skill_dir_name == "principles" else RULE_PATHS
    body = resolve_includes(body, skill_dir, skip_paths=skip)

    desc_lines = description.splitlines()
    if len(desc_lines) > 1:
        desc_yaml = "description: >-\n" + "".join(f"  {ln}\n" for ln in desc_lines)
    else:
        desc_yaml = f"description: {description!r}\n"

    frontmatter = f"---\n{desc_yaml}---\n"
    return frontmatter + "\n" + body


# ── Install / uninstall ───────────────────────────────────────────────────────

# Resolved absolute paths of files already deployed as Cursor rules.
# Commands skip these ! includes to avoid injecting duplicate content.
RULE_PATHS = frozenset(r["source"].resolve() for r in RULES)

SEXTANT_RULE_NAMES   = {r["output_name"] for r in RULES}
SEXTANT_COMMAND_NAMES = {f"{cmd_name}.md" for _, cmd_name in COMMANDS}


def install(target_dir: Path):
    rules_dir    = target_dir / "rules"
    commands_dir = target_dir / "commands"
    rules_dir.mkdir(parents=True, exist_ok=True)
    commands_dir.mkdir(parents=True, exist_ok=True)

    for rule_def in RULES:
        content  = build_rule(rule_def)
        out_path = rules_dir / rule_def["output_name"]
        out_path.write_text(content, encoding="utf-8")
        print(f"  ✓ rules/{rule_def['output_name']}")

    for skill_dir_name, cmd_name in COMMANDS:
        content  = build_command(skill_dir_name)
        out_path = commands_dir / f"{cmd_name}.md"
        out_path.write_text(content, encoding="utf-8")
        print(f"  ✓ commands/{cmd_name}.md")


def uninstall(target_dir: Path):
    removed      = 0
    rules_dir    = target_dir / "rules"
    commands_dir = target_dir / "commands"

    for name in sorted(SEXTANT_RULE_NAMES):
        path = rules_dir / name
        if path.exists():
            path.unlink()
            print(f"  ✗ rules/{name}")
            removed += 1

    for name in sorted(SEXTANT_COMMAND_NAMES):
        path = commands_dir / name
        if path.exists():
            path.unlink()
            print(f"  ✗ commands/{name}")
            removed += 1

    if removed == 0:
        print("  (nothing to remove)")
    else:
        print(f"\n  Removed {removed} file(s).")


# ── Entry point ───────────────────────────────────────────────────────────────

def main():
    args = sys.argv[1:]

    mode   = "install"
    target = None

    for arg in args:
        if arg == "--global":
            target = Path.home() / ".cursor"
        elif arg == "--project":
            target = Path.cwd() / ".cursor"
        elif arg == "--uninstall":
            mode = "uninstall"
        elif arg in ("--help", "-h"):
            print(__doc__)
            sys.exit(0)
        else:
            print(f"Unknown argument: {arg}", file=sys.stderr)
            print("Usage: python .cursor-plugin/install.py [--project|--global] [--uninstall]",
                  file=sys.stderr)
            sys.exit(1)

    if target is None:
        target = Path.cwd() / ".cursor"

    if mode == "uninstall":
        print(f"Uninstalling Sextant from {target} ...")
        uninstall(target)
    else:
        print(f"Installing Sextant for Cursor → {target}")
        install(target)
        print(f"\nDone.")
        if "--global" in args:
            print("Rules and commands are active globally across all Cursor projects.")
            print("Use /sextant-fix-bug, /sextant-add-feature, etc. in any project.")
        else:
            print("Use /sextant-fix-bug, /sextant-add-feature, etc. in Cursor chat.")
            print("Principles are applied automatically to all AI interactions in this project.")


if __name__ == "__main__":
    main()
