# Codex Path Redirect Project Instructions

## Purpose

- Maintain a portable Codex skill for redirecting Codex Desktop project/topic paths after local folders move or are renamed.
- Keep the repository safe to share publicly.

## Key Files

- `SKILL.md`: Agent-facing skill instructions.
- `scripts/redirect_codex_project_path.py`: CLI repair script.
- `references/path-redirect-notes.md`: Detailed operational notes.
- `README.md`: Human-facing bilingual usage guide.

## Commands

- Syntax check: `python -m py_compile scripts/redirect_codex_project_path.py`
- Skill validation: run Codex's local `skill-creator/scripts/quick_validate.py` against the repository root.
- Dry-run example: `python scripts/redirect_codex_project_path.py --old "D:\Projects\OldName" --new "D:\Projects\NewName" --dry-run`

## Working Rules

- Do not commit real `.codex` state, SQLite databases, logs, tokens, session files, backups, or machine-specific paths.
- Use placeholder paths in docs, such as `D:\Projects\OldName` and `D:\Projects\NewName`.
- Keep `SKILL.md` concise and agent-facing; keep user explanation in `README.md`.
- Preserve the CLI flags documented in README unless making a deliberate breaking-change update.
