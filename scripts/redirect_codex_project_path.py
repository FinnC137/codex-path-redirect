#!/usr/bin/env python3
import argparse
import json
import pathlib
import re
import shutil
import sqlite3
import subprocess
import sys
from datetime import datetime


def norm_plain(path: str) -> str:
    value = path.strip().strip('"')
    if value.startswith("\\\\?\\"):
        value = value[4:]
    return str(pathlib.PureWindowsPath(value))


def ext_path(path: str) -> str:
    return "\\\\?\\" + norm_plain(path)


def lower_fwd(path: str) -> str:
    return norm_plain(path).lower().replace("\\", "/")


def replace_path_prefix(value: str, old: str, new: str) -> tuple[str, bool]:
    if value == old:
        return new, True
    if value.startswith(old + "\\"):
        return new + value[len(old):], True
    if value.startswith(old + "/"):
        return new + value[len(old):], True
    return value, False


def text_has_path_ref(text: str, path: str) -> bool:
    plain = re.escape(norm_plain(path))
    escaped = re.escape(norm_plain(path).replace("\\", "\\\\"))
    fwd = re.escape(lower_fwd(path))
    patterns = [
        rf"{plain}(?:\\|/|['\"\]\}}]|$)",
        rf"{escaped}(?:\\\\|/|['\"\]\}}]|$)",
        rf"{fwd}(?:/|['\"\]\}}]|$)",
    ]
    lower = text.lower()
    return any(re.search(pattern.lower(), lower) for pattern in patterns)


class Redirector:
    def __init__(self, codex_home: pathlib.Path, old: str, new: str, dry_run: bool, suffix: str):
        self.codex_home = codex_home
        self.old = norm_plain(old)
        self.new = norm_plain(new)
        self.old_ext = ext_path(old)
        self.new_ext = ext_path(new)
        self.dry_run = dry_run
        self.suffix = suffix
        self.changed = []
        self.warnings = []

    def backup_once(self, path: pathlib.Path) -> None:
        if self.dry_run or not path.exists():
            return
        bak = pathlib.Path(str(path) + self.suffix)
        if not bak.exists():
            shutil.copy2(path, bak)

    def note(self, message: str) -> None:
        self.changed.append(message)

    def write_text(self, path: pathlib.Path, text: str, **kwargs) -> None:
        if not self.dry_run:
            path.write_text(text, **kwargs)

    def rewrite_json_file(self, path: pathlib.Path) -> None:
        if not path.exists():
            return
        text = path.read_text(encoding="utf-8")
        data = json.loads(text)
        touched = False

        for key in [
            "electron-saved-workspace-roots",
            "project-order",
            "pinned-project-ids",
            "active-workspace-roots",
        ]:
            if isinstance(data.get(key), list):
                out = []
                for item in data[key]:
                    if isinstance(item, str):
                        item, replaced = replace_path_prefix(item, self.old, self.new)
                        touched = touched or replaced
                    if item not in out:
                        out.append(item)
                if out != data[key]:
                    data[key] = out
                    touched = True

        labels = data.setdefault("electron-workspace-root-labels", {})
        if self.old in labels:
            labels[self.new] = labels.pop(self.old)
            touched = True
        if self.new not in labels and any(self.new in str(v) for values in data.values() for v in (values if isinstance(values, list) else [])):
            labels[self.new] = pathlib.PureWindowsPath(self.new).name
            touched = True

        if touched:
            self.backup_once(path)
            self.write_text(path, json.dumps(data, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
            self.note(f"{path.name}: sidebar state redirected")

    def rewrite_config(self, path: pathlib.Path) -> None:
        if not path.exists():
            return
        text = path.read_text(encoding="utf-8")
        before = text
        old_header = "[projects.'" + self.old.lower() + "']"
        new_header = "[projects.'" + self.new.lower() + "']"
        if old_header in text:
            text = text.replace(old_header, new_header)
        elif new_header not in text:
            text = text.rstrip() + "\n\n" + new_header + '\ntrust_level = "trusted"\n'
        if text != before:
            self.backup_once(path)
            self.write_text(path, text, encoding="utf-8")
            self.note(f"{path.name}: trust entry redirected")

    def rewrite_cap_sid(self, path: pathlib.Path) -> None:
        if not path.exists():
            return
        obj = json.loads(path.read_text(encoding="utf-8"))
        mapping = obj.get("workspace_by_cwd")
        touched = False
        if isinstance(mapping, dict):
            old_key = lower_fwd(self.old)
            new_key = lower_fwd(self.new)
            for key in list(mapping.keys()):
                if key == old_key or key.startswith(old_key + "/"):
                    mapping[new_key + key[len(old_key):]] = mapping.pop(key)
                    touched = True
        if touched:
            self.backup_once(path)
            self.write_text(path, json.dumps(obj, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
            self.note(f"{path.name}: workspace permission mapping redirected")

    def rewrite_threads_and_rollouts(self, db_path: pathlib.Path) -> None:
        if not db_path.exists():
            self.warnings.append(f"missing database: {db_path}")
            return

        self.backup_once(db_path)
        con = sqlite3.connect(str(db_path))
        cur = con.cursor()
        cur.execute(
            """
            select title, archived, thread_source, cwd, rollout_path
            from threads
            where cwd = ? or cwd like ? or first_user_message like ? or preview like ?
            order by updated_at desc
            """,
            (self.old_ext, self.old_ext + "\\%", f"%{self.old}%", f"%{self.old}%"),
        )
        before_rows = cur.fetchall()

        if not self.dry_run:
            changed_rows = 0
            rows_to_update = cur.execute(
                """
                select id, archived, thread_source, cwd, first_user_message, preview
                from threads
                where cwd = ? or cwd like ? or first_user_message like ? or preview like ?
                """,
                (self.old_ext, self.old_ext + "\\%", f"%{self.old}%", f"%{self.old}%"),
            ).fetchall()
            for row in rows_to_update:
                thread_id, archived, thread_source, cwd, first_user_message, preview = row
                new_cwd, cwd_changed = replace_path_prefix(cwd or "", self.old_ext, self.new_ext)
                new_first = (first_user_message or "").replace(self.old + "\\", self.new + "\\")
                if first_user_message == self.old:
                    new_first = self.new
                new_preview = (preview or "").replace(self.old + "\\", self.new + "\\")
                if preview == self.old:
                    new_preview = self.new
                new_source = thread_source
                if archived == 0 and not thread_source:
                    new_source = "user"
                if (new_cwd, new_first, new_preview, new_source) != (cwd, first_user_message, preview, thread_source):
                    cur.execute(
                        """
                        update threads
                        set cwd = ?, first_user_message = ?, preview = ?, thread_source = ?
                        where id = ?
                        """,
                        (new_cwd, new_first, new_preview, new_source, thread_id),
                    )
                    changed_rows += 1
            con.commit()
            try:
                con.execute("pragma wal_checkpoint(full)")
            except sqlite3.DatabaseError:
                pass
        else:
            changed_rows = len(before_rows)

        rows = cur.execute(
            "select title, rollout_path from threads where cwd = ? and archived = 0",
            (self.new_ext,),
        ).fetchall()
        con.close()

        if changed_rows:
            self.note(f"{db_path.name}: {changed_rows} thread row(s) redirected")

        rollout_count = 0
        for title, rollout_path in rows:
            path = pathlib.Path(rollout_path)
            if not path.exists():
                self.warnings.append(f"missing rollout for {title}: {path}")
                continue
            lines = path.read_text(encoding="utf-8", errors="surrogateescape").splitlines(True)
            if not lines:
                continue
            meta = json.loads(lines[0])
            if meta.get("type") != "session_meta" or not isinstance(meta.get("payload"), dict):
                continue
            payload = meta["payload"]
            before = dict(payload)
            current_cwd = str(payload.get("cwd", self.new))
            payload["cwd"], replaced = replace_path_prefix(current_cwd, self.old, self.new)
            if not replaced and current_cwd == self.old_ext:
                payload["cwd"] = self.new
            if not payload.get("thread_source"):
                payload["thread_source"] = "user"
            if payload != before:
                rollout_count += 1
                self.backup_once(path)
                if not self.dry_run:
                    lines[0] = json.dumps(meta, ensure_ascii=False, separators=(",", ":")) + "\n"
                    path.write_text("".join(lines), encoding="utf-8", errors="surrogateescape")
        if rollout_count:
            self.note(f"rollout jsonl: {rollout_count} session_meta line(s) redirected")

    def run(self) -> None:
        self.rewrite_threads_and_rollouts(self.codex_home / "state_5.sqlite")
        self.rewrite_json_file(self.codex_home / ".codex-global-state.json")
        self.rewrite_json_file(self.codex_home / ".codex-global-state.json.bak")
        self.rewrite_config(self.codex_home / "config.toml")
        self.rewrite_cap_sid(self.codex_home / "cap_sid")

    def verify(self) -> int:
        old_hits = []
        new_hits = []
        for name in [".codex-global-state.json", ".codex-global-state.json.bak", "config.toml", "cap_sid"]:
            path = self.codex_home / name
            if path.exists():
                text = path.read_text(encoding="utf-8", errors="surrogateescape")
                if text_has_path_ref(text, self.old):
                    old_hits.append(name)
                if text_has_path_ref(text, self.new):
                    new_hits.append(name)

        db_path = self.codex_home / "state_5.sqlite"
        db_rows = []
        rollout_bad = []
        if db_path.exists():
            con = sqlite3.connect(str(db_path))
            rows = con.execute(
                """
                select title, archived, thread_source, cwd, rollout_path
                from threads
                where cwd = ? or cwd like ? or cwd = ? or cwd like ? or first_user_message like ? or preview like ?
                order by updated_at desc
                """,
                (self.old_ext, self.old_ext + "\\%", self.new_ext, self.new_ext + "\\%", f"%{self.old}%", f"%{self.old}%"),
            ).fetchall()
            con.close()
            for row in rows:
                title, archived, thread_source, cwd, rollout_path = row
                db_rows.append((title, archived, thread_source, cwd))
                path = pathlib.Path(rollout_path)
                if path.exists() and archived == 0 and self.new in cwd:
                    meta = json.loads(path.read_text(encoding="utf-8", errors="surrogateescape").splitlines()[0])
                    payload = meta.get("payload", {})
                    if payload.get("cwd") != self.new or not payload.get("thread_source"):
                        rollout_bad.append((title, payload.get("cwd"), payload.get("thread_source")))

        print("Verification")
        print("old references in files:", old_hits or "none")
        print("new references in files:", new_hits or "none")
        print("matching db rows:")
        for row in db_rows:
            print(" -", row)
        if rollout_bad:
            print("rollout metadata needing attention:")
            for row in rollout_bad:
                print(" -", row)
        return 1 if old_hits or rollout_bad else 0


def codex_pids() -> list[int]:
    if sys.platform != "win32":
        return []
    try:
        result = subprocess.run(
            [
                "powershell",
                "-NoProfile",
                "-Command",
                "Get-Process | Where-Object { $_.ProcessName -like 'Codex*' -or $_.ProcessName -eq 'codex' } | Select-Object -ExpandProperty Id",
            ],
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError:
        return []
    ids = []
    for line in result.stdout.splitlines():
        line = line.strip()
        if line.isdigit():
            ids.append(int(line))
    return ids


def install_after_exit_watcher(args: argparse.Namespace) -> None:
    pids = codex_pids()
    if not pids:
        print("No running Codex processes found; watcher not needed.")
        return
    script = pathlib.Path(__file__).resolve()
    quoted = " ".join(
        [
            f'"{sys.executable}"',
            f'"{script}"',
            "--old",
            json.dumps(args.old),
            "--new",
            json.dumps(args.new),
            "--codex-home",
            json.dumps(str(args.codex_home)),
        ]
    )
    pid_csv = ",".join(str(pid) for pid in pids)
    ps = f"""
$ids = @({pid_csv})
$deadline = (Get-Date).AddMinutes(15)
while ((Get-Date) -lt $deadline) {{
  $alive = @($ids | ForEach-Object {{ Get-Process -Id $_ -ErrorAction SilentlyContinue }})
  if ($alive.Count -eq 0) {{ break }}
  Start-Sleep -Seconds 2
}}
Start-Sleep -Seconds 2
{quoted}
"""
    watcher = pathlib.Path.home() / ".codex" / "tmp" / "codex_project_path_redirect_after_exit.ps1"
    watcher.parent.mkdir(parents=True, exist_ok=True)
    watcher.write_text(ps, encoding="utf-8")
    subprocess.Popen(
        ["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(watcher)],
        creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0,
    )
    print("Started after-exit watcher for Codex PIDs:", pid_csv)


def main() -> int:
    parser = argparse.ArgumentParser(description="Redirect Codex Desktop project/thread paths.")
    parser.add_argument("--old", required=True, help="Old plain Windows path.")
    parser.add_argument("--new", required=True, help="New plain Windows path.")
    parser.add_argument("--codex-home", type=pathlib.Path, default=pathlib.Path.home() / ".codex")
    parser.add_argument("--dry-run", action="store_true", help="Show intended changes without writing.")
    parser.add_argument("--verify-only", action="store_true", help="Only verify the redirect state.")
    parser.add_argument("--allow-missing-new", action="store_true", help="Do not fail when --new does not exist.")
    parser.add_argument("--install-after-exit-watcher", action="store_true", help="Run again after current Codex processes exit.")
    args = parser.parse_args()

    suffix = ".path-redirect-" + datetime.now().strftime("%Y%m%d%H%M%S") + ".bak"
    redirector = Redirector(args.codex_home, args.old, args.new, args.dry_run, suffix)

    if not args.allow_missing_new and not pathlib.Path(redirector.new).exists():
        print(f"New path does not exist: {redirector.new}", file=sys.stderr)
        return 2

    if args.verify_only:
        return redirector.verify()

    redirector.run()
    print("old =", redirector.old)
    print("new =", redirector.new)
    print("mode =", "dry-run" if args.dry_run else "write")
    print("changes:")
    for item in redirector.changed:
        print(" -", item)
    if not redirector.changed:
        print(" - none")
    if redirector.warnings:
        print("warnings:")
        for item in redirector.warnings:
            print(" -", item)

    rc = redirector.verify()
    if args.install_after_exit_watcher and not args.dry_run:
        install_after_exit_watcher(args)
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
