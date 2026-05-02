import json
from pathlib import Path

APP_NAME = "Tiny Pomodoro"
APP_ID = "tiny-pomodoro-xfce"

CONFIG_DIR = Path.home() / ".config" / APP_ID
CONFIG_FILE = CONFIG_DIR / "config.json"

AUTOSTART_DIR = Path.home() / ".config" / "autostart"
AUTOSTART_FILE = AUTOSTART_DIR / "tiny-pomodoro.desktop"

DEFAULTS = {
    "timer_title": "Pomodoro",
    "work_minutes": 25,
    "short_break_minutes": 5,
    "long_break_minutes": 15,
    "cycles_before_long_break": 4,
    "short_break_message": "Time to stand up, stretch your shoulders, back, neck and wrists.",
    "long_break_message": "Long break. Walk a bit, drink water, breathe, and reset your posture.",
    "work_message": "Back to focus. Start the next work session.",
    "auto_start_break": False,
    "auto_start_work": False,

    "timer_title_custom": "Timer",
    "timer_hours": 0,
    "timer_minutes": 10,
    "timer_seconds": 0,
    "timer_finished_message": "The countdown timer has finished.",
    "timer_shutdown": False,
    "timer_shutdown_delay_seconds": 30,

    "always_on_top": True,
    "x": 80,
    "y": 80,
    "size": 210,
    "opacity": 0.96,
    "dim_when_inactive": False,
    "inactive_opacity": 0.72,
    "compact_mode": False,
    "notify": True,
    "sound": False,
    "sound_file": "",
    "theme": "system",
    "animations": True,
    "autostart": False,
}


def load_config():
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    if CONFIG_FILE.exists():
        try:
            data = json.loads(CONFIG_FILE.read_text())
            return {**DEFAULTS, **data}
        except Exception:
            return dict(DEFAULTS)
    return dict(DEFAULTS)


def save_config(config):
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps(config, indent=2))


def sync_autostart(enabled, app_path):
    AUTOSTART_DIR.mkdir(parents=True, exist_ok=True)

    if enabled:
        AUTOSTART_FILE.write_text(f"""[Desktop Entry]
Type=Application
Name=Tiny Pomodoro
Comment=Tiny Pomodoro timer
Exec={app_path}
Icon=appointment-soon
Terminal=false
Categories=Utility;
""")
    elif AUTOSTART_FILE.exists():
        AUTOSTART_FILE.unlink()
