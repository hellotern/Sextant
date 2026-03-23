#!/usr/bin/env python3
"""
Sextant UserPromptSubmit hook.

Detects coding-related prompts and injects Sextant engineering principles
as a system message, so Claude applies them without any manual configuration.
"""
import json
import os
import re
import sys

# Verbs that signal an actionable coding task
_TASK_VERBS = {
    "fix", "debug", "implement", "refactor", "review", "optimize",
    "test", "write", "add", "create", "update", "modify", "change",
    "improve", "build", "develop", "extend", "enhance", "rewrite",
    "migrate", "integrate", "deploy", "analyse", "analyze", "design",
    "restructure", "cleanup", "clean", "simplify", "extract", "split",
    "merge", "resolve", "handle", "validate", "parse", "generate",
    # Chinese equivalents (pinyin won't appear, but unicode CJK may)
    "修复", "实现", "重构", "优化", "测试", "添加", "创建", "更新",
    "修改", "改进", "构建", "开发", "扩展", "迁移", "分析", "设计",
}

# Nouns that confirm a technical/code context
_CODE_NOUNS = {
    "code", "function", "method", "class", "module", "component",
    "feature", "bug", "test", "api", "endpoint", "service", "repo",
    "repository", "interface", "pr", "pull request", "refactor",
    "codebase", "library", "package", "dependency", "import",
    "database", "query", "schema", "migration", "route", "handler",
    "controller", "model", "view", "hook", "middleware", "plugin",
    "script", "pipeline", "workflow", "ci", "cd", "lint", "type",
    "error", "exception", "log", "config", "env",
    # Chinese
    "代码", "函数", "方法", "类", "模块", "组件", "功能", "漏洞",
    "接口", "数据库", "配置", "服务", "仓库",
}


def is_coding_task(prompt: str) -> bool:
    """Return True when the prompt looks like a hands-on coding request."""
    # Latin: match on word tokens
    words = set(re.findall(r"[a-zA-Z_]\w*", prompt.lower()))
    if words & _TASK_VERBS or words & _CODE_NOUNS:
        return True
    # CJK: Chinese has no spaces, so check substring membership directly
    for kw in _TASK_VERBS | _CODE_NOUNS:
        if "\u4e00" <= kw[0] <= "\u9fff" and kw in prompt:
            return True
    return False


def load_skill(plugin_root: str) -> str:
    """Load SKILL.md and replace relative reference paths with absolute ones."""
    skill_path = os.path.join(plugin_root, "skills", "principles", "SKILL.md")
    if not os.path.exists(skill_path):
        return ""

    with open(skill_path, encoding="utf-8") as fh:
        content = fh.read()

    # Make reference file paths absolute so Claude's Read tool can locate them.
    # Single-pass str.replace is safe: Python does not re-scan substituted text.
    refs_abs = os.path.join(plugin_root, "skills", "principles", "references")
    content = content.replace("references/", refs_abs + "/")

    return content


def main() -> None:
    try:
        input_data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    prompt = input_data.get("prompt", "")
    if not prompt.strip() or not is_coding_task(prompt):
        print("{}")
        sys.exit(0)

    plugin_root = os.environ.get("CLAUDE_PLUGIN_ROOT", "")
    if not plugin_root:
        print("{}")
        sys.exit(0)

    skill_content = load_skill(plugin_root)
    if not skill_content:
        print("{}")
        sys.exit(0)

    print(json.dumps({"systemMessage": skill_content}))
    sys.exit(0)


if __name__ == "__main__":
    main()
