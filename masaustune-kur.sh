#!/usr/bin/env bash
set -euo pipefail
base="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
export BASE="$base"
exec /usr/bin/python3 - <<'PY'
import os
import shlex
import shutil
import stat
import subprocess
import tempfile
from pathlib import Path

base = Path(os.environ["BASE"])
uid = os.getuid()
if uid == 0 or os.geteuid() != uid:
    raise SystemExit("Kurucuyu normal kullanıcı olarak, sudo olmadan çalıştır.")

def absolute(value):
    path = Path(value)
    if not path.is_absolute():
        raise SystemExit(f"Kurulum yolu mutlak olmalı: {path}")
    return Path(os.path.abspath(path))

home = absolute(Path.home())
data = absolute(os.environ.get("XDG_DATA_HOME") or home / ".local/share")
app = data / "ajan-atolyesi"
menu = data / "applications" / "ajan-atolyesi.desktop"
desktop_value = (subprocess.check_output(["xdg-user-dir", "DESKTOP"], text=True).strip()
                 if shutil.which("xdg-user-dir") else str(home / "Desktop"))
desktop = absolute(desktop_value) if desktop_value else home
shortcut = desktop / "Ajan Atölyesi.desktop"
identity = app / ".ajan-atolyesi"
launcher = app / "ac"
metadata = app / ".ajan-surum-bilgisi"
marker = "X-Ajan-Atolyesi=true"
files = ("bin/ajan-pencere", "bin/evren-dsh-terminal", "bin/ajan-dsh",
         "bin/ajan-dsh-pane", "bin/ajan-kur", "bin/ajan-atolyesi", "bin/ajan-surum",
         "bin/evren-baglanti-kontrol", "VERSION", "CHANGELOG.md", "LICENSE", "SECURITY.md",
         "README.md",
         "BASLA.md", "CONTRIBUTING.md", "KURULUM-PROMPTU.md", "DOGRULAMA-PROMPTU.md", "docs/evren-dsh.md",
         "docs/sss.md", "docs/linux.md", "docs/macos.md", "docs/windows.md",
         "docs/manuel-kurulum.md", "docs/kalite.md", "demo/GOREV.md",
         "demo/slug.py", "demo/test_slug.py", "assets/ajan-atolyesi.svg")

def reject(path):
    raise SystemExit(f"Güvenli olmayan kurulum yolu; hiçbir dosya yazılmadı: {path}")

def inspect(path):
    try:
        return path.lstat()
    except FileNotFoundError:
        return None

system_owners = {0, Path("/").stat().st_uid}  # Includes mapped system IDs.
checked = set()
shared_parents = set()
def check_dirs(path):
    for part in (*reversed(path.parents), path):
        if part in checked:
            continue
        st = inspect(part)
        if st is None and part.parent in shared_parents:
            # A not-yet-owned name below a shared temp directory may be claimed.
            reject(part)
        if st is not None:
            sticky_root = st.st_uid in system_owners and bool(st.st_mode & stat.S_ISVTX)
            if (not stat.S_ISDIR(st.st_mode) or
                    (st.st_uid != uid and st.st_uid not in system_owners) or
                    (st.st_mode & 0o022 and not sticky_root)):
                reject(part)
            if st.st_mode & 0o022:
                shared_parents.add(part)
        checked.add(part)

def check_file(path):
    check_dirs(path.parent)
    st = inspect(path)
    if st is not None and (not stat.S_ISREG(st.st_mode) or st.st_uid != uid):
        reject(path)
    return st

# Validate all affected leaves and their ancestors before creating or replacing anything.
check_dirs(app)
app_stat = inspect(app)
if app_stat is not None and (app_stat.st_uid != uid or not check_file(identity)):
    raise SystemExit(f"Mevcut klasöre dokunulmadı: {app}")
has_shortcut = False
if desktop != home:
    check_dirs(desktop)
    has_shortcut = inspect(desktop) is not None

for target in (menu, shortcut) if has_shortcut else (menu,):
    if check_file(target):
        fd = os.open(target, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
        with os.fdopen(fd, "r", encoding="utf-8") as handle:
            st = os.fstat(handle.fileno())
            if not stat.S_ISREG(st.st_mode) or st.st_uid != uid:
                reject(target)
            prior = handle.read(128 * 1024)
        old = f'Exec="{home}/.local/bin/ajan-atolyesi-masaustu"'
        if marker not in prior.splitlines() and old not in prior.splitlines():
            raise SystemExit(f"Bu kısayola dokunulmadı: {target}")

for target in (identity, launcher, metadata, *(app / relative for relative in files)):
    check_file(target)

version_data = subprocess.check_output(["bash", str(base / "bin/ajan-surum"), "--metadata"])
os.umask(0o022)

def write_atomic(path, writer, mode):
    path.parent.mkdir(mode=0o755, parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=".ajan-kur-", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as output:
            writer(output)
            os.fchmod(output.fileno(), mode)
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)

def write_contents(path, data, mode=0o644):
    write_atomic(path, lambda out: out.write(data), mode)

def copy_item(relative):
    mode = 0o755 if relative.startswith("bin/") else 0o644
    with (base / relative).open("rb") as source:
        write_atomic(app / relative, lambda out: shutil.copyfileobj(source, out), mode)

app.mkdir(mode=0o700, parents=True, exist_ok=True)
if app_stat is None:
    write_contents(identity, b"")
for item in files:
    copy_item(item)
write_contents(metadata, version_data, 0o600)
launcher_body = ('#!/bin/sh\nexport PATH="$HOME/.local/bin:$HOME/bin:$PATH"\n'
                 'cd "$HOME" || exit 1\nexec ' + shlex.quote(str(app / "bin/ajan-pencere")) + ' "$@"\n')
write_contents(launcher, launcher_body.encode("utf-8"), 0o755)

# Exec has Desktop Entry escaping plus its own argument-quoting rules.
def desktop_arg(path):
    arg = str(path).replace("%", "%%")
    for old, new in [("\\", "\\\\"), ('"', '\\"'), ("`", "\\`"), ("$", "\\$")]:
        arg = arg.replace(old, new)
    return '"' + arg.replace("\\", "\\\\") + '"'

entry = ("[Desktop Entry]\nType=Application\nName=Ajan Atölyesi\n"
         f"Exec={desktop_arg(launcher)}\n"
         f"Icon={app / 'assets/ajan-atolyesi.svg'}\n"
         f"Terminal=false\nStartupWMClass=ajan-atolyesi\nCategories=Development;\n{marker}\n")
write_contents(menu, entry.encode("utf-8"))
if has_shortcut:
    write_contents(shortcut, entry.encode("utf-8"), 0o755)
    if not shutil.which("gio") or subprocess.run(
            ["gio", "set", "-t", "string", str(shortcut), "metadata::trusted", "true"],
            capture_output=True).returncode:
        print("Masaüstünde gerekirse sağ tık → Başlatmaya izin ver.")
print("Ajan Atölyesi kuruldu. Uygulama menüsünden açabilirsin.")
PY
