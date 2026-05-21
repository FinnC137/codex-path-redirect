# Codex Path Redirect Notes

Codex Desktop keeps local project/thread state in multiple files under `~/.codex`.

Important locations:

- `state_5.sqlite`: main thread database. `threads.cwd` usually stores paths with a Windows extended prefix, for example `\\?\D:\Projects\Example`.
- `sessions/**/rollout-*.jsonl`: the first line is a `session_meta` JSON object; its `payload.cwd` uses the plain Windows path.
- `.codex-global-state.json`: Electron sidebar workspace roots, ordering, labels, and active roots.
- `.codex-global-state.json.bak`: often mirrors the same sidebar information.
- `config.toml`: trusted project entries under `[projects.'lowercase-path']`.
- `cap_sid`: JSON permission mapping under `workspace_by_cwd`, usually using lowercase forward-slash paths.

Operational notes:

- A visible historical thread may disappear from a project if database `cwd`, rollout `session_meta.cwd`, and `thread_source` disagree.
- For unarchived local user threads, blank or null `thread_source` should be set to `user`.
- Archived threads do not normally show in the regular project list; do not unarchive unless requested.
- If Codex is running, its in-memory sidebar state can rewrite `.codex-global-state.json` on exit. Use an after-exit watcher for repairs made while Codex is open.
- Chinese or renamed Windows paths can leave stale plain paths in JSON/JSONL even when SQLite has the extended path form.

Minimal manual query:

```powershell
python -c "import pathlib,sqlite3; db=pathlib.Path.home()/'.codex'/'state_5.sqlite'; con=sqlite3.connect(str(db)); [print(r) for r in con.execute('select title, archived, thread_source, cwd, rollout_path from threads where cwd like ? or title like ? order by updated_at desc', ('%OLD_OR_NEW_FRAGMENT%','%TITLE_FRAGMENT%')).fetchall()]"
```
