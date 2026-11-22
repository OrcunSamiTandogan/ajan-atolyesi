"""GTK integration check: empty state, provider save, Pi install and session.
Uses fake CLI binaries and fake keys. Does not contact any provider.
"""
import os
from pathlib import Path
import runpy
import tempfile

import gi
gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
gi.require_version("Vte", "2.91")
from gi.repository import Gdk, Gio, GLib, Gtk, Vte

import sys
source = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parents[1] / "bin/ajan-pencere"


def children(widget):
    yield widget
    if isinstance(widget, Gtk.Container):
        for child in widget.get_children():
            yield from children(child)


def button(parent, label):
    return next(w for w in children(parent) if isinstance(w, Gtk.Button) and w.get_label() == label)


def until(predicate, timeout_us=5_000_000):
    end = GLib.get_monotonic_time() + timeout_us
    context = GLib.MainContext.default()
    while not predicate() and GLib.get_monotonic_time() < end:
        while context.pending():
            context.iteration(False)
        GLib.usleep(10_000)
    assert predicate()


assert Gtk.init_check()[0]
with tempfile.TemporaryDirectory() as tmp:
    folder = Path(tmp)
    fake_bin = folder / "bin"
    fake_bin.mkdir()
    saved_home = os.environ.get("HOME")
    os.environ.update(HOME=tmp, PATH=str(fake_bin), XDG_CONFIG_HOME=str(folder / "config"))
    os.chdir(tmp)
    app = runpy.run_path(str(source))
    window, controls, stack = app["make_window"](Gtk, Vte, Gio, GLib)
    assert stack.get_visible_child_name() == "start"

    def check_about():
        dialog = next(w for w in Gtk.Window.list_toplevels() if isinstance(w, Gtk.AboutDialog) and w.get_visible())
        assert dialog.get_website() == app["REPO_URL"]
        assert "DeepSeek Harness" in dialog.get_comments() and dialog.get_logo() is not None
        dialog.response(Gtk.ResponseType.CLOSE)
        return GLib.SOURCE_REMOVE
    GLib.idle_add(check_about)
    next(w for w in children(window) if isinstance(w, Gtk.Button)
         and w.get_tooltip_text() == "Ajan Atölyesi hakkında").clicked()

    def check_faq():
        dialog = next(w for w in Gtk.Window.list_toplevels()
                      if isinstance(w, Gtk.Dialog) and w.get_visible() and w.get_title() == "Sık sorulan sorular")
        view = next(w for w in children(dialog) if isinstance(w, Gtk.TextView))
        buf = view.get_buffer()
        text = buf.get_text(*buf.get_bounds(), False)
        assert "NVIDIA" in text and "EVREN" in text
        dialog.response(Gtk.ResponseType.CLOSE)
        return GLib.SOURCE_REMOVE
    GLib.idle_add(check_faq)
    button(window, "Sık sorulan sorular").clicked()

    for variable, label, fake_key in (("NVIDIA_API_KEY", "NVIDIA anahtarı", "nvapi-fake_key_12345"),
                                      ("EVREN_API_KEY", "EVREN anahtarı", "evren_fake_key")):
        key_button = button(window, label)
        dot = key_button.get_parent().get_children()[1]
        assert "#343943" in dot.get_label()
        assert "Henüz girilmedi" in dot.get_tooltip_text()

        def fill():
            dialog = next(w for w in Gtk.Window.list_toplevels() if isinstance(w, Gtk.Dialog) and w.get_visible())
            entry = next(w for w in children(dialog) if isinstance(w, Gtk.Entry))
            assert not entry.get_visibility()
            entry.set_text(fake_key)
            dialog.response(Gtk.ResponseType.OK)
            return GLib.SOURCE_REMOVE
        GLib.idle_add(fill)
        key_button.clicked()
        assert app["key_file_status"]()[variable] == "Kayıtlı"
        assert "#62DEA0" in dot.get_label() or "#087546" in dot.get_label()
        assert "Kayıtlı" in dot.get_tooltip_text()

    def check_status_dialog():
        dialog = next(w for w in Gtk.Window.list_toplevels() if isinstance(w, Gtk.Dialog) and w.get_visible())
        labels = {w.get_text(): w.get_label() for w in children(dialog) if isinstance(w, Gtk.Label)}
        for provider in ("NVIDIA", "EVREN"):
            status_markup = labels[f"{provider}: Kayıtlı"]
            assert "semibold" in status_markup and ("#62DEA0" in status_markup or "#087546" in status_markup)
        dialog.response(Gtk.ResponseType.CLOSE)
        return GLib.SOURCE_REMOVE

    GLib.idle_add(check_status_dialog)
    button(window, "Atölye anahtarları (.env)").clicked()
    assert not (folder / ".env").exists()

    # A real dialog and VTE launch, with fake tmux and fake agent executables.
    for binary, target in (("bash", "/bin/bash"), ("dirname", "/usr/bin/dirname"), ("cat", "/bin/cat")):
        (fake_bin / binary).symlink_to(target)
    for agent in ("claude", "codex"):
        executable = fake_bin / agent
        executable.write_text('#!/bin/sh\nprintf "%s" "$1" > "$HOME/' + agent + '-setup-prompt"\n/bin/sleep 1\n')
        executable.chmod(0o700)
    fake_setup_tmux = fake_bin / "tmux"
    fake_setup_tmux.write_text("""#!/bin/sh
case "$1" in
  has-session) exit 1 ;;
  new-session)
    while [ "$#" -ge 2 ] && [ "$2" != "--pane" ]; do shift; done
    [ "$2" = "--pane" ] || exit 2
    exec "$@" ;;
  *) exit 1 ;;
esac
""")
    fake_setup_tmux.chmod(0o700)
    os.environ.pop("TMUX", None)

    def setup_response(option, response):
        dialog = next(w for w in Gtk.Window.list_toplevels() if isinstance(w, Gtk.Dialog)
                      and w.get_visible() and w.get_title() == "Kurulum seçenekleri")
        choices = [w for w in children(dialog) if isinstance(w, Gtk.CheckButton)]
        assert [w.get_label() for w in choices] == ["Pi + NVIDIA", "EVREN + DeepSeek (DSH CLI ve Web)"]
        assert not any(w.get_active() for w in choices)
        normal = dialog.get_widget_for_response(Gtk.ResponseType.OK)
        unsafe = dialog.get_widget_for_response(Gtk.ResponseType.APPLY)
        assert not normal.get_sensitive() and unsafe is None
        if option is not None:
            choices[option].set_active(True)
            assert normal.get_sensitive()
        dialog.response(response)
        return GLib.SOURCE_REMOVE

    GLib.idle_add(setup_response, None, Gtk.ResponseType.CANCEL)
    button(window, "Claude ile kur").clicked()
    assert not (folder / "claude-setup-prompt").exists()
    for name, agent, option, chosen, excluded in (
        ("Claude ile kur", "claude", 0, "Pi + NVIDIA", "EVREN"),
        ("Codex ile kur", "codex", 1, "EVREN + DeepSeek", "NVIDIA"),
    ):
        GLib.idle_add(setup_response, option, Gtk.ResponseType.OK)
        button(window, name).clicked()
        receipt = folder / (agent + "-setup-prompt")
        until(receipt.exists)
        contents = receipt.read_text()
        assert chosen in contents and excluded not in contents and "tekrar seçim sorma" in contents
    fake_setup_tmux.unlink()

    # One exact tmux target, with a similarly named sibling as a decoy.
    tmux = fake_bin / "tmux"
    folder_a, folder_b = folder / "proje-a", folder / "proje-b"
    folder_a.mkdir()
    folder_b.mkdir()
    tmux.write_text(
        "#!/bin/sh\n"
        'case "$1" in\n'
        "list-sessions) printf '%s\\n' 'aa-codex $7' 'aa-claude-old $8' 'aa-evren-cli $9' ;;\n"
        f"display-message) printf '%s\\n' '{folder_a}' ;;\n"
        'has-session) test "$3" = "=aa-codex" ;;\n'
        'show-environment) case "$4" in AA_ATOLYE_OWNER) printf "AA_ATOLYE_OWNER=ajan-atolyesi-public-v1\\n";; AA_SETUP_MODE) printf "AA_SETUP_MODE=normal\\n";; esac ;;\n'
        "attach-session) /bin/sleep 2 ;;\n"
        "*) exit 1 ;;\nesac\n"
    )
    tmux.chmod(0o700)
    def check_reminder_dialog():
        dialog = next(w for w in Gtk.Window.list_toplevels()
                      if isinstance(w, Gtk.Dialog) and w.get_visible() and w.get_title() == "Oturum hatırlatıcısı")
        view = next(w for w in children(dialog) if isinstance(w, Gtk.TextView))
        buffer = view.get_buffer()
        body = buffer.get_text(*buffer.get_bounds(), False)
        assert "tmux hedefleri: aa-codex, aa-evren-cli." in body
        assert "aa-claude-old" not in body
        dialog.response(Gtk.ResponseType.OK)
        return GLib.SOURCE_REMOVE

    GLib.idle_add(check_reminder_dialog)
    reminder = next(w for w in children(window) if isinstance(w, Gtk.Button)
                    and w.get_tooltip_text() == "Oturum hatırlatıcısı")
    reminder.clicked()
    assert "test veya başka sunucudaki" in Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD).wait_for_text()
    for name, target in (("Codex oturumu", "aa-codex"), ("Claude oturumu", None),
                         ("Pi · NVIDIA", None), ("EVREN · DSH CLI", "aa-evren-cli"), ("EVREN · DSH Web", None)):
        row = button(window, name)
        assert row.emit("popup-menu")
        menu = Gtk.Menu.get_for_attach_widget(row)[0]
        item = next(w for w in menu.get_children() if w.get_label() == "Oturum kimliğini kopyala")
        assert item.get_sensitive() == bool(target)
        if target:
            assert item.get_tooltip_text() == f"Açık panelin klasörü: {folder_a}"
            item.activate()
            assert Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD).wait_for_text() == target
        menu.destroy()

    chooser = next(w for w in children(window) if isinstance(w, Gtk.FileChooserButton))
    chooser.set_filename(str(folder_b))
    button(window, "Codex oturumu").clicked()
    assert any(isinstance(w, Gtk.Label) and w.get_visible() and
               w.get_text() == "Açık oturum başka klasörde: proje-a" for w in children(window))

    pi = button(window, "Pi · NVIDIA")
    pi.clicked()
    assert stack.get_visible_child_name() == "pi-install"
    install = button(stack.get_visible_child(), "Pi’yi kur")
    assert app["pi_install_command"]() is None
    node = fake_bin / "node"
    node.write_text("#!/bin/sh\nprintf '%s\\n' v24.22.2\n")
    node.chmod(0o700)
    npm = fake_bin / "npm"
    npm.write_text("""#!/bin/sh
set -eu
test -z "${NVIDIA_API_KEY:-}${EVREN_API_KEY:-}"
while [ "$1" != --prefix ]; do shift; done
/bin/mkdir -p "$2/bin"
cat_path="$2/bin/pi"
/bin/cat > "$cat_path" <<'PI'
#!/bin/sh
if [ "${1:-}" = --version ]; then printf '%s\\n' 1.6.0; exit 0; fi
test -n "$NVIDIA_API_KEY"
test -z "${EVREN_API_KEY:-}"
printf 'MOCK_PI_READY\\n'
printf "%s" "$PWD" > "$HOME/config/mock-pi-ready"
/bin/sleep 3
PI
/bin/chmod 700 "$cat_path"
""")
    npm.chmod(0o700)
    install.clicked()
    until(lambda: stack.get_visible_child_name() == "start" and app["pi_binary"]())
    chooser = next(w for w in children(window) if isinstance(w, Gtk.FileChooserButton))
    chooser.set_filename(tmp)

    def confirm_pi(response):
        dialog = next(w for w in Gtk.Window.list_toplevels() if isinstance(w, Gtk.Dialog)
                      and w.get_visible() and w.get_title() == "Pi · NVIDIA güvenilir klasör")
        labels = " ".join(w.get_text() for w in children(dialog) if isinstance(w, Gtk.Label))
        assert "NVIDIA anahtarına erişebilir" in labels and tmp in labels
        assert "nvapi-fake_key_12345" not in labels
        dialog.response(response)
        return GLib.SOURCE_REMOVE

    GLib.idle_add(confirm_pi, Gtk.ResponseType.CANCEL)
    pi.clicked()
    assert stack.get_visible_child_name() != "pi"
    assert not (folder / "config/mock-pi-ready").exists()
    GLib.idle_add(confirm_pi, Gtk.ResponseType.OK)
    pi.clicked()
    assert stack.get_visible_child_name() == "pi"
    terminal = stack.get_visible_child().get_child()
    until(lambda: terminal.get_pty() is not None and (folder / "config/mock-pi-ready").exists())
    assert (folder / "config/mock-pi-ready").read_text() == tmp
    button(window, "EVREN · DSH Web").clicked()
    assert stack.get_visible_child_name() == "evren-setup"
    assert button(stack.get_visible_child(), "dsh’yi kur").get_visible()

    fake_dsh = fake_bin / "dsh"
    marker = folder / "evren-wrapper-started"
    fake_dsh.write_text(
        "#!/bin/sh\n"
        "if [ \"$1\" = --version ]; then printf '%s\\n' 0.2.2-rc.5; exit 0; fi\n"
        "test \"$1 $2\" = '--profile web' || exit 2\n"
        "test \"$5 $6 $7 $8 $9\" = '--host 127.0.0.1 --port 0 --no-open' || exit 3\n"
        f"/usr/bin/touch '{marker}'\n"
        "/bin/sleep 2\n"
    )
    fake_dsh.chmod(0o700)
    button(window, "EVREN · DSH Web").clicked()
    assert stack.get_visible_child_name() == "evren"
    terminal = stack.get_visible_child().get_child()
    until(lambda: terminal.get_pty() is not None and marker.exists())
    # The final row opens an interactive shell in the selected directory.
    shell = fake_bin / "test-shell"
    shell_marker = folder / "terminal-started"
    shell.write_text(
        "#!/bin/sh\n"
        "test \"$1\" = -i || exit 2\n"
        f"printf '%s' \"$PWD\" > '{shell_marker}'\n"
        "/bin/sleep 2\n"
    )
    shell.chmod(0o700)
    os.environ["SHELL"] = str(shell)
    button(window, "Terminal").clicked()
    assert stack.get_visible_child_name() == "terminal"
    terminal = stack.get_visible_child().get_child()
    until(lambda: terminal.get_pty() is not None and shell_marker.exists())
    assert shell_marker.read_text() == tmp
    window.hide()
    if saved_home:
        os.environ["HOME"] = saved_home

print("GTK: kurulum seçimleri ve gerçek prompt aktarımı → temiz ayar → maskeli anahtarlar → Pi kurulumu → Pi terminali → EVREN kurulum ekranı ve resmî dsh web çağrısı geçti (sahte CLI/anahtar).")
