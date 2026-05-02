import subprocess
from pathlib import Path

from .config import APP_NAME


def notify(config, title, body):
    if config["notify"]:
        subprocess.Popen(["notify-send", "-a", APP_NAME, title, body])

    if config["sound"]:
        custom = config.get("sound_file", "").strip()
        if custom and Path(custom).exists():
            subprocess.Popen(["paplay", custom])
        else:
            subprocess.Popen(["paplay", "/usr/share/sounds/freedesktop/stereo/complete.oga"])
