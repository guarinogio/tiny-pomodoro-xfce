import subprocess
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk


def system_is_dark():
    try:
        theme = subprocess.check_output(
            ["xfconf-query", "-c", "xsettings", "-p", "/Net/ThemeName"],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip().lower()
        if "dark" in theme:
            return True
    except Exception:
        pass

    try:
        settings = Gtk.Settings.get_default()
        return bool(settings.get_property("gtk-application-prefer-dark-theme"))
    except Exception:
        return False


def is_dark(config):
    if config["theme"] == "dark":
        return True
    if config["theme"] == "light":
        return False
    return system_is_dark()


def install_window_css(config):
    if is_dark(config):
        bg = "#1f2227"
        fg = "#e8edf2"
        border = "rgba(255,255,255,0.10)"
        hover = "rgba(255,255,255,0.10)"
    else:
        bg = "#f7f7f7"
        fg = "#1f2937"
        border = "rgba(0,0,0,0.14)"
        hover = "rgba(0,0,0,0.08)"

    css = f"""
    window {{ background-color: transparent; }}
    .app {{
        background: {bg};
        border: 1px solid {border};
        border-radius: 16px;
        box-shadow: 0 8px 24px rgba(0,0,0,0.25);
    }}
    button {{
        border: none;
        box-shadow: none;
        background: transparent;
        color: {fg};
        font-size: 16px;
        padding: 2px 8px;
        text-shadow: none;
        outline: none;
    }}
    button:hover {{
        background: {hover};
        border-radius: 9px;
    }}
    button:active {{ background: rgba(127,127,127,0.18); }}
    """.encode()

    provider = Gtk.CssProvider()
    provider.load_from_data(css)
    Gtk.StyleContext.add_provider_for_screen(
        Gdk.Screen.get_default(),
        provider,
        Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
    )


def colors(config, mode):
    if is_dark(config):
        base = {
            "bg": (0.12, 0.13, 0.15),
            "fg": (0.91, 0.93, 0.95),
            "track": (1, 1, 1, 0.12),
        }
    else:
        base = {
            "bg": (0.97, 0.97, 0.97),
            "fg": (0.12, 0.16, 0.22),
            "track": (0, 0, 0, 0.10),
        }

    if mode == "work":
        ring = (0.82, 0.86, 0.92) if is_dark(config) else (0.28, 0.28, 0.28)
    elif mode == "short_break":
        ring = (0.45, 0.75, 0.58)
    elif mode == "long_break":
        ring = (0.48, 0.64, 0.92)
    else:
        ring = (0.90, 0.70, 0.35)

    base["ring"] = ring
    return base
