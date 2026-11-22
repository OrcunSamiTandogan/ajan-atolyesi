#!/bin/bash
set -eu
[ "$(uname -s)" = Darwin ] || { printf 'Bu kurucu macOS için.\n' >&2; exit 1; }
src="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
uid="$(id -u)"
[ "$uid" != 0 ] && [ "$uid" = "$(id -ru)" ] || {
  printf 'Kurucuyu normal kullanıcı olarak, sudo olmadan çalıştır.\n' >&2
  exit 1
}
reject() {
  printf 'Güvenli olmayan kurulum yolu: %s\n' "$1" >&2
  exit 1
}
case "$HOME" in /*) ;; *) reject "$HOME";; esac
[ ! -L "$HOME" ] || reject "$HOME"
# Resolve standard macOS aliases above HOME (e.g. /var -> /private/var).
home="$(cd -P -- "$HOME" && pwd)"
app="$home/Applications/Ajan Atölyesi.app"
contents="$app/Contents"
marker="$contents/.ajan-atolyesi"
resources="$contents/Resources"
executable="$contents/MacOS/ajan-atolyesi"
plist="$contents/Info.plist"
meta="$resources/.ajan-surum-bilgisi"
exec_files=(bin/ajan-pencere bin/evren-dsh-terminal bin/ajan-dsh bin/ajan-dsh-pane
            bin/ajan-kur bin/ajan-atolyesi bin/ajan-surum bin/evren-baglanti-kontrol)
data_files=(VERSION CHANGELOG.md LICENSE SECURITY.md README.md BASLA.md CONTRIBUTING.md KURULUM-PROMPTU.md DOGRULAMA-PROMPTU.md
            docs/{evren-dsh,sss,linux,macos,windows,manuel-kurulum,kalite}.md
            assets/ajan-atolyesi.svg demo/GOREV.md demo/slug.py demo/test_slug.py)

stat_details() {
  local details
  if details="$(stat -f '%u %p' "$1" 2>/dev/null)"; then
    printf '%s\n' "$details"
  else
    stat -c '%u %a' -- "$1" 2>/dev/null
  fi
}
system_details="$(stat_details /)" || reject /
system_owner="${system_details%% *}"
check_dir() {
  local path="$1" details owner octal rest
  [ ! -L "$path" ] || reject "$path"
  if [ ! -e "$path" ]; then
    # Claim only names below trusted parents, not in shared temporary roots.
    if details="$(stat_details "${path%/*}")"; then
      read -r owner octal rest <<< "$details"
      [[ "$octal" =~ ^[0-7]+$ ]] || reject "$path"
      (( (8#$octal & 0022) == 0 )) || reject "$path"
    fi
    return 0
  fi
  [ -d "$path" ] || reject "$path"
  details="$(stat_details "$path")" || reject "$path"
  read -r owner octal rest <<< "$details"
  [[ "$owner" = "$uid" || "$owner" = 0 || "$owner" = "$system_owner" ]] || reject "$path"
  [[ "$octal" =~ ^[0-7]+$ ]] || reject "$path"
  if (( (8#$octal & 0022) != 0 )); then
    [[ ( "$owner" = 0 || "$owner" = "$system_owner" ) && $((8#$octal & 01000)) -ne 0 ]] || reject "$path"
  fi
}
check_file() {
  [ ! -L "$1" ] || reject "$1"
  [ ! -e "$1" ] || { [ -f "$1" ] && [ -O "$1" ]; } || reject "$1"
}
check_ancestors() {
  case "$1" in
    /) check_dir / ;;
    *) local parent="${1%/*}"; check_ancestors "${parent:-/}"; check_dir "$1" ;;
  esac
}
# Check parents from the root down, then all managed leaves before any write.
check_ancestors "$home"
for path in "$home/Applications" "$app" "$contents" "$contents/MacOS" "$resources" \
  "$resources/bin" "$resources/docs" "$resources/assets" "$resources/demo"; do
  check_dir "$path"
done
check_file "$marker"
if [ -e "$app" ] && { [ ! -O "$app" ] || [ ! -f "$marker" ]; }; then
  printf 'Bu addaki mevcut uygulamaya dokunulmadı: %s\n' "$app" >&2
  exit 1
fi
for path in "$executable" "$plist" "$meta" "$resources/ajan-atolyesi.icns"; do
  check_file "$path"
done
for file in "${exec_files[@]}" "${data_files[@]}"; do check_file "$resources/$file"; done

version_data="$(bash "$src/bin/ajan-surum" --metadata)"
semantic_version="$(bash "$src/bin/ajan-surum" --version)"
build_number="$(bash "$src/bin/ajan-surum" --build)"
bundle_build=""
if [ -n "$build_number" ]; then
  bundle_build="<key>CFBundleVersion</key><string>$build_number</string>"
fi

umask 022
mkdir -p "$contents/MacOS" "$resources"
for folder in bin docs assets demo; do mkdir -p "$resources/$folder"; done
staged=
trap 'if [ -n "$staged" ]; then rm -f -- "$staged"; fi' EXIT
new_file() {
  staged="$(mktemp "${1%/*}/.ajan-kur.XXXXXX")"
}
finish_file() {
  chmod "$2" "$staged"
  check_file "$1"
  mv -f "$staged" "$1"
  staged=
}
copy_file() {
  new_file "$2"
  cat "$1" > "$staged"
  finish_file "$2" "$3"
}
if [ ! -f "$marker" ]; then new_file "$marker"; finish_file "$marker" 644; fi
for file in "${exec_files[@]}"; do copy_file "$src/$file" "$resources/$file" 755; done
for file in "${data_files[@]}"; do copy_file "$src/$file" "$resources/$file" 644; done
copy_file "$src/assets/ajan-atolyesi.icns" "$resources/ajan-atolyesi.icns" 644
new_file "$meta"
printf '%s\n' "$version_data" > "$staged"
finish_file "$meta" 600
new_file "$plist"
cat > "$staged" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "https://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
<key>CFBundleName</key><string>Ajan Atölyesi</string>
<key>CFBundleDisplayName</key><string>Ajan Atölyesi</string>
<key>CFBundleIdentifier</key><string>io.github.orcunsamitandogan.ajan-atolyesi</string>
<key>CFBundlePackageType</key><string>APPL</string>
<key>CFBundleExecutable</key><string>ajan-atolyesi</string>
<key>CFBundleIconFile</key><string>ajan-atolyesi.icns</string>
<key>CFBundleShortVersionString</key><string>$semantic_version</string>
$bundle_build
</dict></plist>
PLIST
finish_file "$plist" 644
new_file "$executable"
cat > "$staged" <<'LAUNCH'
#!/bin/bash
set -eu
contents="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
if [ "${1:-}" = --version ]; then
  exec "$contents/Resources/bin/ajan-surum" --display
fi
check_deps=0
[ "${1:-}" != --check-deps ] || check_deps=1
report() {
  printf '%s\n' "$1" >&2
  if [ "$check_deps" -eq 0 ] && [ -x /usr/bin/osascript ]; then
    /usr/bin/osascript - "$1" <<'APPLESCRIPT' >/dev/null || true
on run argv
  display alert "Ajan Atölyesi" message (item 1 of argv)
end run
APPLESCRIPT
  fi
  exit 1
}
export PATH="$HOME/.local/bin:$HOME/bin:/opt/homebrew/bin:/usr/local/bin:$PATH"
brew="$(command -v brew)" || report "Homebrew kurulu değil. Önce https://brew.sh adresinden kur."
prefix="$("$brew" --prefix)" || report "Homebrew kurulum konumu bulunamadı."
for formula in gtk+3 vte3 pygobject3 tmux; do
  "$brew" list --versions "$formula" >/dev/null 2>&1 ||
    report "Eksik paket: $formula. Terminalde brew install gtk+3 vte3 pygobject3 tmux çalıştır."
done
export PATH="$prefix/bin:$PATH"
[ -x "$prefix/bin/tmux" ] || report "Homebrew tmux komutu bulunamadı. Homebrew bağlantılarını kontrol et."
export GI_TYPELIB_PATH="$prefix/lib/girepository-1.0:$prefix/opt/gtk+3/lib/girepository-1.0:$prefix/opt/vte3/lib/girepository-1.0${GI_TYPELIB_PATH:+:$GI_TYPELIB_PATH}"
cd "$HOME"
for py in "$prefix/bin/python3" "$prefix"/opt/python@*/bin/python3.*; do
  [ -x "$py" ] || continue
  case "$py" in *-config) continue;; esac
  if "$py" -c 'import gi; gi.require_version("Gtk", "3.0"); gi.require_version("Vte", "2.91"); from gi.repository import Gtk, Vte' 2>/dev/null; then
    if [ "$check_deps" -eq 1 ]; then
      printf 'Bağımlılıklar hazır: %s · GTK 3 · VTE 2.91 · tmux\n' "$py"
      exit 0
    fi
    exec "$py" "$contents/Resources/bin/ajan-pencere" "$@"
  fi
done
report "Homebrew Python ile GTK 3 ve VTE 2.91 yüklenemedi. Terminalde uygulamayı --check-deps ile kontrol et; macOS rehberindeki paketlere bak."
LAUNCH
finish_file "$executable" 755
printf 'Kuruldu: %s\nFinder → Ev → Applications → Ajan Atölyesi\n' "$app"
