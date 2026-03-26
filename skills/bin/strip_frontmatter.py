#!/usr/bin/env python3
"""Strip YAML frontmatter from a Markdown file and print the body."""
import sys, os


def strip_frontmatter(filepath):
    """Output the body of a Markdown file after its YAML frontmatter.

    Matches awk 'f;/^---$/{c++}c==2{f=1}' behavior exactly:
    - Prints lines only after the second '---'.
    - If the file has fewer than two '---' delimiters, outputs nothing.
    """
    with open(filepath, encoding='utf-8') as f:
        lines = f.readlines()
    count = 0
    for i, line in enumerate(lines):
        if line.strip() == '---':
            count += 1
            if count == 2:
                sys.stdout.write(''.join(lines[i + 1:]))
                return
    # No second '---' found → output nothing (matches awk behavior)


if __name__ == '__main__':
    # Usage: strip_frontmatter.py <file> [--if-dir-exists <dir>]
    # Requires Python 3. If `python3` is not in PATH, invoke via `python` instead.
    silent_on_error = False

    if '--if-dir-exists' in sys.argv:
        # Mirrors: [ -d <dir> ] && awk ... || true
        # The || true means ALL failures are swallowed, including missing files.
        silent_on_error = True
        idx = sys.argv.index('--if-dir-exists')
        guard_dir = sys.argv[idx + 1]
        if not os.path.isdir(guard_dir):
            sys.exit(0)
        filepath = sys.argv[1]
    else:
        filepath = sys.argv[1]

    try:
        strip_frontmatter(os.path.expandvars(filepath))
    except OSError:
        if not silent_on_error:
            raise
