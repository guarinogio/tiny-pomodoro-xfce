#!/usr/bin/env bash
set -euo pipefail

APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BIN_DIR="$HOME/.local/bin"
DESKTOP_DIR="$HOME/.local/share/applications"

sudo apt update
sudo apt install -y python3-gi gir1.2-gtk-3.0 gir1.2-pango-1.0 libnotify-bin pulseaudio-utils xfconf

mkdir -p "$BIN_DIR" "$DESKTOP_DIR"

cat > "$BIN_DIR/tiny-pomodoro" <<EOF
#!/usr/bin/env bash
cd "$APP_DIR"
exec "$APP_DIR/tiny_pomodoro.py"
EOF
chmod +x "$BIN_DIR/tiny-pomodoro"

cat > "$DESKTOP_DIR/tiny-pomodoro.desktop" <<EOF
[Desktop Entry]
Type=Application
Name=Tiny Pomodoro
Comment=Small Pomodoro and countdown timer for XFCE
Exec=$BIN_DIR/tiny-pomodoro
Icon=appointment-soon
Terminal=false
Categories=Utility;
EOF

chmod +x "$DESKTOP_DIR/tiny-pomodoro.desktop"
update-desktop-database "$DESKTOP_DIR" 2>/dev/null || true

echo "Installed. Run: tiny-pomodoro"
