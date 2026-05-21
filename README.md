# Codex Path Redirect

English | [中文](#中文)

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

## 中文

这是一个 Codex skill，用来修复 Codex Desktop 里的项目/话题路径。当项目目录被移动、重命名，或者中文路径编码异常导致历史话题还挂在旧目录下时，它会把相关本地状态统一指向新路径。

仓库地址：<https://github.com/FinnC137/codex-path-redirect>

## 适用场景

适合这些情况：

- 项目文件夹移动或改名后，Codex 侧栏仍显示旧路径；
- 中文或非 ASCII 路径导致工作目录异常；
- 历史话题挂在不存在的目录下面；
- 希望旧话题重新出现在新的项目路径下面。

## 安装为 Codex Skill

克隆仓库：

```powershell
git clone https://github.com/FinnC137/codex-path-redirect.git
```

复制到 Codex skills 目录：

```powershell
New-Item -ItemType Directory -Force "$HOME\.codex\skills" | Out-Null
Copy-Item -Recurse -Force ".\codex-path-redirect" "$HOME\.codex\skills\codex-path-redirect"
```

重启 Codex Desktop，让它重新发现这个 skill。

## 使用方式

先 dry-run：

```powershell
python "$HOME\.codex\skills\codex-path-redirect\scripts\redirect_codex_project_path.py" --old "D:\Projects\OldName" --new "D:\Projects\NewName" --dry-run
```

正式修复：

```powershell
python "$HOME\.codex\skills\codex-path-redirect\scripts\redirect_codex_project_path.py" --old "D:\Projects\OldName" --new "D:\Projects\NewName"
```

修复后验证：

```powershell
python "$HOME\.codex\skills\codex-path-redirect\scripts\redirect_codex_project_path.py" --old "D:\Projects\OldName" --new "D:\Projects\NewName" --verify-only
```

如果 Codex Desktop 正在运行，建议先关闭所有 Codex 窗口再执行；也可以使用退出后 watcher，避免 Codex 退出时把旧侧栏状态写回：

```powershell
python "$HOME\.codex\skills\codex-path-redirect\scripts\redirect_codex_project_path.py" --old "D:\Projects\OldName" --new "D:\Projects\NewName" --install-after-exit-watcher
```

## 会修改什么

- `~/.codex/state_5.sqlite`
- `~/.codex/sessions/**/rollout-*.jsonl`
- `~/.codex/.codex-global-state.json`
- `~/.codex/.codex-global-state.json.bak`
- `~/.codex/config.toml`
- `~/.codex/cap_sid`

脚本写入前会自动生成带时间戳的备份。

## 安全建议

- 一定先用 `--dry-run` 看计划改哪些内容。
- 默认要求新路径存在；如果你确实要指向尚未创建的路径，再加 `--allow-missing-new`。
- 不建议手动直接改 Codex 本地状态文件，除非你已经做好备份。
- Codex Desktop 正在运行时，退出时可能把侧栏状态写回旧值；这种情况用 watcher，或者关闭后再跑一次。

## License

MIT
