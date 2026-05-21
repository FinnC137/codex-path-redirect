# Codex Path Redirect

English | [??](#??)

A small Codex skill for repairing Codex Desktop project paths after a local folder is moved, renamed, or affected by a broken/encoded Windows path. It updates the sidebar project entry, historical topic/thread ownership, rollout metadata, trust config, and workspace permission mapping together.

Repository: <https://github.com/FinnC137/codex-path-redirect>

## When To Use

Use this when Codex Desktop still shows a project or topic under an old path after:

- moving or renaming a project folder;
- fixing a Chinese/non-ASCII path issue;
- seeing historical topics attached to a missing directory;
- needing a topic to appear under the new project path in Codex Desktop.

## Install As A Codex Skill

Clone the repository:

```powershell
git clone https://github.com/FinnC137/codex-path-redirect.git
```

Install it into your Codex skills directory:

```powershell
New-Item -ItemType Directory -Force "$HOME\.codex\skills" | Out-Null
Copy-Item -Recurse -Force ".\codex-path-redirect" "$HOME\.codex\skills\codex-path-redirect"
```

Restart Codex Desktop so the skill is discoverable.

## Usage

Run a dry run first:

```powershell
python "$HOME\.codex\skills\codex-path-redirect\scripts\redirect_codex_project_path.py" --old "D:\Projects\OldName" --new "D:\Projects\NewName" --dry-run
```

Run the redirect:

```powershell
python "$HOME\.codex\skills\codex-path-redirect\scripts\redirect_codex_project_path.py" --old "D:\Projects\OldName" --new "D:\Projects\NewName"
```

Verify afterwards:

```powershell
python "$HOME\.codex\skills\codex-path-redirect\scripts\redirect_codex_project_path.py" --old "D:\Projects\OldName" --new "D:\Projects\NewName" --verify-only
```

If Codex Desktop is currently running, either close all Codex windows before running the redirect, or install an after-exit watcher:

```powershell
python "$HOME\.codex\skills\codex-path-redirect\scripts\redirect_codex_project_path.py" --old "D:\Projects\OldName" --new "D:\Projects\NewName" --install-after-exit-watcher
```

## What It Updates

- `~/.codex/state_5.sqlite`
- `~/.codex/sessions/**/rollout-*.jsonl`
- `~/.codex/.codex-global-state.json`
- `~/.codex/.codex-global-state.json.bak`
- `~/.codex/config.toml`
- `~/.codex/cap_sid`

The script creates timestamped backups before writing.

## Safety

- Always start with `--dry-run`.
- Make sure the new path exists, unless you intentionally pass `--allow-missing-new`.
- Do not edit live Codex state by hand unless you have backups.
- If Codex Desktop is running, it may rewrite sidebar state on exit; use the watcher or rerun after closing Codex.

## ??

???? Codex skill????? Codex Desktop ????/????????????????????????????????????????????????????????????

?????<https://github.com/FinnC137/codex-path-redirect>

## ????

???????

- ????????????Codex ?????????
- ???? ASCII ???????????
- ???????????????
- ???????????????????

## ??? Codex Skill

?????

```powershell
git clone https://github.com/FinnC137/codex-path-redirect.git
```

??? Codex skills ???

```powershell
New-Item -ItemType Directory -Force "$HOME\.codex\skills" | Out-Null
Copy-Item -Recurse -Force ".\codex-path-redirect" "$HOME\.codex\skills\codex-path-redirect"
```

?? Codex Desktop????????? skill?

## ????

? dry-run?

```powershell
python "$HOME\.codex\skills\codex-path-redirect\scripts\redirect_codex_project_path.py" --old "D:\Projects\OldName" --new "D:\Projects\NewName" --dry-run
```

?????

```powershell
python "$HOME\.codex\skills\codex-path-redirect\scripts\redirect_codex_project_path.py" --old "D:\Projects\OldName" --new "D:\Projects\NewName"
```

??????

```powershell
python "$HOME\.codex\skills\codex-path-redirect\scripts\redirect_codex_project_path.py" --old "D:\Projects\OldName" --new "D:\Projects\NewName" --verify-only
```

?? Codex Desktop ???????????? Codex ?????????????? watcher??? Codex ????????????

```powershell
python "$HOME\.codex\skills\codex-path-redirect\scripts\redirect_codex_project_path.py" --old "D:\Projects\OldName" --new "D:\Projects\NewName" --install-after-exit-watcher
```

## ?????

- `~/.codex/state_5.sqlite`
- `~/.codex/sessions/**/rollout-*.jsonl`
- `~/.codex/.codex-global-state.json`
- `~/.codex/.codex-global-state.json.bak`
- `~/.codex/config.toml`
- `~/.codex/cap_sid`

??????????????????

## ????

- ???? `--dry-run` ?????????
- ???????????????????????????? `--allow-missing-new`?
- ???????? Codex ?????????????????
- Codex Desktop ?????????????????????????? watcher???????????

## License

MIT
