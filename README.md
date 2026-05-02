# Tiny Pomodoro XFCE

Tiny Pomodoro XFCE is a small floating Pomodoro and countdown timer for Xubuntu/XFCE.

It is designed for people who want a lightweight, always-visible productivity timer with a clean GTK interface, system notifications, dark mode support, and an installable Debian package.

## Features

- Pomodoro mode
- Countdown timer mode
- Small floating GTK window
- Always-on-top toggle
- Dedicated drag button
- System notifications
- Optional sound
- Custom sound file
- XFCE dark mode detection
- Manual light/dark theme override
- Smooth progress ring animation
- Different ring colors by mode
- Auto-start options for Pomodoro phases
- Timer hours/minutes/seconds
- Optional system shutdown when timer finishes
- Shutdown cancellation button
- Optional autostart with session
- Installable `.deb`
- Public APT repository via GitHub Pages

## Install with APT

Add the signing key:

```bash
curl -fsSL https://guarinogio.github.io/tiny-pomodoro-xfce-apt/public.key \
  | sudo gpg --dearmor --yes -o /usr/share/keyrings/tiny-pomodoro-xfce.gpg
```

Add the APT source:

```bash
echo "deb [arch=all signed-by=/usr/share/keyrings/tiny-pomodoro-xfce.gpg] https://guarinogio.github.io/tiny-pomodoro-xfce-apt stable main" \
  | sudo tee /etc/apt/sources.list.d/tiny-pomodoro-xfce.list
```

Install:

```bash
sudo apt update
sudo apt install tiny-pomodoro-xfce
```

Run:

```bash
tiny-pomodoro
```

## Manual install from source

```bash
git clone https://github.com/guarinogio/tiny-pomodoro-xfce.git
cd tiny-pomodoro-xfce
./install.sh
```

Then run:

```bash
tiny-pomodoro
```

## Development

Install build dependencies:

```bash
sudo apt install -y \
  python3-gi gir1.2-gtk-3.0 gir1.2-pango-1.0 \
  libnotify-bin pulseaudio-utils xfconf \
  devscripts debhelper dh-python python3-all \
  pybuild-plugin-pyproject python3-setuptools \
  desktop-file-utils python3-pytest
```

Run from source:

```bash
./tiny_pomodoro.py
```

Run tests:

```bash
./smoke_test.sh
```

Build a Debian package:

```bash
dpkg-buildpackage -us -uc -b
```

Install the generated package:

```bash
sudo apt install ../tiny-pomodoro-xfce_VERSION_all.deb
```

## Release workflow

Versioning is managed with `bump2version`.

```bash
bump2version patch
git push --follow-tags
```

Pushing a version tag triggers the GitHub Actions workflow that builds the `.deb`, uploads it to the GitHub release, and publishes it to the public APT repository.

## Configuration

User configuration is stored at:

```bash
~/.config/tiny-pomodoro-xfce/config.json
```

## Shutdown safety

The shutdown feature is disabled by default.

To enable shutdown after timer completion, the Timer settings require explicit confirmation. When triggered, shutdown is scheduled and can be cancelled from the app or manually:

```bash
shutdown -c
```

## Project links

- Project repository: https://github.com/guarinogio/tiny-pomodoro-xfce
- APT repository: https://github.com/guarinogio/tiny-pomodoro-xfce-apt
- Project site: https://guarinogio.github.io/tiny-pomodoro-xfce/

## License

MIT
