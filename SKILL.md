---
name: codex-path-redirect
description: Redirect Codex Desktop project paths and historical threads after a local folder is moved, renamed, or fixed from a broken/encoded Windows path. Use when Codex needs to repair sidebar project entries, topic/thread history location, session rollout cwd metadata, config trust entries, or cap_sid workspace mappings from an old local path to a new path.
---

# Codex Path Redirect

## Workflow

Use this skill when a Codex Desktop project or topic still appears under an old path in the sidebar/history after its folder has moved.

Prefer the bundled script:

```powershell
python "$HOME\.codex\skills\codex-path-redirect\scripts\redirect_codex_project_path.py" --old "OLD_PATH" --new "NEW_PATH"
```

Run a dry run first when the target is unclear:

```powershell
python "$HOME\.codex\skills\codex-path-redirect\scripts\redirect_codex_project_path.py" --old "OLD_PATH" --new "NEW_PATH" --dry-run
```

If only a topic title is known, first inspect matching records in `~/.codex/state_5.sqlite` and infer the old path from the matching `threads.cwd`; then run the script with the exact old and new paths.

## What To Update

Codex stores a project path in several places. A complete redirect updates:

- `state_5.sqlite`: `threads.cwd`, `first_user_message`, `preview`, and blank visible `thread_source`.
- `rollout-*.jsonl`: first-line `session_meta.payload.cwd` and `thread_source`.
- `.codex-global-state.json` and `.codex-global-state.json.bak`: sidebar roots, project order, active roots, pinned ids, labels.
- `config.toml`: trusted project header.
- `cap_sid`: workspace permission mapping.

Only changing `.codex-global-state.json` or `config.toml` is not enough.

## Safety Rules

- Confirm `--new` exists before modifying unless the user explicitly wants a pre-created future path.
- Use `--dry-run` before broad path replacements.
- Let the script create backups; do not overwrite or delete existing backups.
- Keep the old and new paths as plain Windows paths, for example `D:\Projects\OldName`; the script handles the SQLite `\\?\` prefix.
- If Codex Desktop is running, run the script now and also use `--install-after-exit-watcher`, or tell the user to close all Codex windows and rerun. Running Codex may rewrite sidebar state on exit.

## Validation

After redirecting, verify:

```powershell
python "$HOME\.codex\skills\codex-path-redirect\scripts\redirect_codex_project_path.py" --old "OLD_PATH" --new "NEW_PATH" --verify-only
```

Expected:

- matching unarchived threads have `cwd` under the new path;
- visible local threads have `thread_source = user`;
- matching rollout first lines have `payload.cwd` set to the new path;
- sidebar state and trust/permission files no longer point at the old path.

## Reference

For the reasoning behind the procedure and manual troubleshooting notes, read `references/path-redirect-notes.md`.
