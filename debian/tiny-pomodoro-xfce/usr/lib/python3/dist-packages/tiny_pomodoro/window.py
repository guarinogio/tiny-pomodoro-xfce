import math
import subprocess
import time
from pathlib import Path

import gi

gi.require_version("Gtk", "3.0")
gi.require_version("PangoCairo", "1.0")
from gi.repository import Gtk, Gdk, GLib, Pango, PangoCairo

from .config import APP_NAME, load_config, save_config, sync_autostart
from .dialogs import PomodoroSettingsDialog, TimerSettingsDialog
from .notifications import notify
from .theme import install_window_css, colors


class PomodoroWindow(Gtk.Window):
    def __init__(self, app_path):
        super().__init__(title=APP_NAME)

        self.app_path = Path(app_path).resolve()
        self.config = load_config()

        self.app_mode = "pomodoro"
        self.mode = "work"
        self.cycle_count = 0
        self.running = False
        self.shutdown_scheduled = False
        self.shutdown_deadline = None

        self.remaining = self.config["work_minutes"] * 60
        self.total = self.remaining
        self.last_tick = time.monotonic()
        self.visual_progress = 0.0

        self.setup_window()
        self.build_ui()
        self.apply_theme()
        sync_autostart(self.config["autostart"], self.app_path)

        GLib.timeout_add(250, self.tick)
        GLib.timeout_add(16, self.animate)

        self.show_all()
        self.apply_window_geometry()
        self.cancel_shutdown_btn.hide()

    def setup_window(self):
        self.set_decorated(False)
        self.set_resizable(False)
        self.set_app_paintable(True)
        self.set_skip_taskbar_hint(True)
        self.set_skip_pager_hint(True)
        self.set_type_hint(Gdk.WindowTypeHint.UTILITY)
        self.set_keep_above(self.config["always_on_top"])
        self.set_opacity(self.config["opacity"])
        size = self.current_window_size()
        self.set_default_size(size, size + 42)
        self.move(self.config.get("x", 80), self.config.get("y", 80))

        self.connect("delete-event", self.on_delete)
        self.connect("configure-event", self.on_configure)
        self.connect("button-press-event", self.on_right_click)
        self.connect("focus-in-event", self.on_focus_in)
        self.connect("focus-out-event", self.on_focus_out)
        self.connect("enter-notify-event", self.on_pointer_in)
        self.connect("leave-notify-event", self.on_pointer_out)

    def build_ui(self):
        self.root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.root.get_style_context().add_class("app")
        self.add(self.root)

        self.header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
        self.header.set_size_request(-1, 28)
        self.header.set_margin_start(8)
        self.header.set_margin_end(8)
        self.header.set_margin_top(4)
        self.root.pack_start(self.header, False, False, 0)

        self.pin_btn = Gtk.Button(label="⇧" if self.config["always_on_top"] else "○")
        self.pin_btn.set_tooltip_text("Toggle always on top")
        self.pin_btn.connect("clicked", self.toggle_top)
        self.header.pack_start(self.pin_btn, False, False, 0)

        self.drag_btn = Gtk.Button(label="↕")
        self.drag_btn.set_tooltip_text("Hold and drag to move")
        self.drag_btn.connect("button-press-event", self.start_drag)
        self.header.pack_start(self.drag_btn, False, False, 0)

        self.header.pack_start(Gtk.Box(), True, True, 0)

        self.opts = Gtk.Button(label="⚙")
        self.opts.set_tooltip_text("Settings")
        self.opts.connect("clicked", self.open_settings)
        self.header.pack_start(self.opts, False, False, 0)

        self.close_top = Gtk.Button(label="×")
        self.close_top.set_tooltip_text("Close")
        self.close_top.connect("clicked", lambda *_: self.destroy())
        self.header.pack_start(self.close_top, False, False, 0)

        self.area = Gtk.DrawingArea()
        self.area.set_size_request(self.config["size"], self.config["size"])
        self.area.connect("draw", self.draw)
        self.root.pack_start(self.area, True, True, 0)

        self.controls = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=18)
        self.controls.set_halign(Gtk.Align.CENTER)
        self.controls.set_homogeneous(True)
        self.controls.set_margin_start(28)
        self.controls.set_margin_end(28)
        self.controls.set_margin_bottom(10)
        self.root.pack_start(self.controls, False, False, 0)

        self.play = Gtk.Button(label="▶")
        self.play.set_tooltip_text("Start / pause")
        self.play.connect("clicked", self.toggle)
        self.controls.pack_start(self.play, True, True, 0)

        self.stop = Gtk.Button(label="■")
        self.stop.set_tooltip_text("Reset current period")
        self.stop.connect("clicked", self.reset_current)
        self.controls.pack_start(self.stop, True, True, 0)

        self.reset_btn = Gtk.Button(label="↺")
        self.reset_btn.set_tooltip_text("Reset Pomodoro")
        self.reset_btn.connect("clicked", self.reset_pomodoro)
        self.controls.pack_start(self.reset_btn, True, True, 0)

        self.timer_btn = Gtk.Button(label="T")
        self.timer_btn.set_tooltip_text("Switch to timer mode")
        self.timer_btn.connect("clicked", self.toggle_timer_mode)
        self.controls.pack_start(self.timer_btn, True, True, 0)

        self.cancel_shutdown_btn = Gtk.Button(label="P×")
        self.cancel_shutdown_btn.set_tooltip_text("Cancel scheduled shutdown")
        self.cancel_shutdown_btn.connect("clicked", self.cancel_shutdown)
        self.controls.pack_start(self.cancel_shutdown_btn, True, True, 0)

    def apply_theme(self):
        install_window_css(self.config)
        self.area.queue_draw()

    def current_window_size(self):
        return 170 if self.config.get("compact_mode") else self.config["size"]

    def apply_window_geometry(self):
        size = self.current_window_size()
        self.resize(size, size + 42)
        self.area.set_size_request(size, size)
        self.set_opacity(self.config["opacity"])

        if self.config.get("compact_mode"):
            self.stop.hide()
            self.reset_btn.hide()
        else:
            self.stop.show()
            self.reset_btn.show()

    def apply_active_opacity(self):
        self.set_opacity(self.config["opacity"])

    def apply_inactive_opacity(self):
        if self.config.get("dim_when_inactive"):
            self.set_opacity(self.config["inactive_opacity"])

    def on_focus_in(self, *_):
        self.apply_active_opacity()
        return False

    def on_focus_out(self, *_):
        self.apply_inactive_opacity()
        return False

    def on_pointer_in(self, *_):
        self.apply_active_opacity()
        return False

    def on_pointer_out(self, *_):
        self.apply_inactive_opacity()
        return False

    def save(self):
        save_config(self.config)

    def timer_total_seconds(self):
        return (
            self.config["timer_hours"] * 3600
            + self.config["timer_minutes"] * 60
            + self.config["timer_seconds"]
        ) or 60

    def on_configure(self, *_):
        try:
            x, y = self.get_position()
            self.config["x"] = x
            self.config["y"] = y
            self.save()
        except Exception:
            pass

    def on_delete(self, *_):
        self.save()
        return False

    def start_drag(self, _widget, event):
        self.begin_move_drag(event.button, int(event.x_root), int(event.y_root), event.time)
        return True

    def toggle_top(self, *_):
        self.config["always_on_top"] = not self.config["always_on_top"]
        self.set_keep_above(self.config["always_on_top"])
        self.pin_btn.set_label("⇧" if self.config["always_on_top"] else "○")
        self.save()

    def toggle(self, *_):
        if self.remaining <= 0:
            self.remaining = self.total
            self.visual_progress = 0.0

        self.running = not self.running
        self.last_tick = time.monotonic()
        self.play.set_label("Ⅱ" if self.running else "▶")

    def reset_current(self, *_):
        self.running = False
        self.play.set_label("▶")
        self.remaining = self.total
        self.visual_progress = 0.0
        self.area.queue_draw()

    def reset_pomodoro(self, *_):
        self.cancel_shutdown()
        self.app_mode = "pomodoro"
        self.mode = "work"
        self.cycle_count = 0
        self.running = False
        self.play.set_label("▶")
        self.timer_btn.set_label("T")
        self.timer_btn.set_tooltip_text("Switch to timer mode")
        self.total = self.config["work_minutes"] * 60
        self.remaining = self.total
        self.visual_progress = 0.0
        self.area.queue_draw()

    def toggle_timer_mode(self, *_):
        self.running = False
        self.play.set_label("▶")
        self.cancel_shutdown()

        if self.app_mode == "pomodoro":
            self.app_mode = "timer"
            self.mode = "timer"
            self.timer_btn.set_label("P")
            self.timer_btn.set_tooltip_text("Switch to Pomodoro mode")
            self.total = self.timer_total_seconds()
            self.remaining = self.total
            self.visual_progress = 0.0
        else:
            self.reset_pomodoro()

        self.area.queue_draw()

    def open_settings(self, *_):
        dialog = TimerSettingsDialog(self) if self.app_mode == "timer" else PomodoroSettingsDialog(self)
        response = dialog.run()

        if response == Gtk.ResponseType.OK:
            self.config.update(dialog.get_values())
            self.save()
            sync_autostart(self.config["autostart"], self.app_path)

            self.set_keep_above(self.config["always_on_top"])
            self.pin_btn.set_label("⇧" if self.config["always_on_top"] else "○")
            self.set_opacity(self.config["opacity"])
            self.resize(self.config["size"], self.config["size"] + 42)
            self.area.set_size_request(self.config["size"], self.config["size"])

            if self.mode == "timer":
                self.total = self.timer_total_seconds()
            elif self.mode == "work":
                self.total = self.config["work_minutes"] * 60
            elif self.mode == "short_break":
                self.total = self.config["short_break_minutes"] * 60
            else:
                self.total = self.config["long_break_minutes"] * 60

            self.remaining = min(self.remaining, self.total)
            self.apply_theme()
            self.area.queue_draw()

        dialog.destroy()

    def tick(self):
        if self.running:
            now = time.monotonic()
            elapsed = now - self.last_tick
            self.last_tick = now
            self.remaining -= elapsed

            if self.remaining <= 0:
                self.finish_period()

            self.area.queue_draw()
        else:
            self.last_tick = time.monotonic()

        if self.shutdown_scheduled and self.shutdown_deadline:
            if time.monotonic() >= self.shutdown_deadline:
                self.shutdown_scheduled = False
                self.cancel_shutdown_btn.hide()

        return True

    def animate(self):
        if not self.config["animations"]:
            return True

        target = 1 - max(0, self.remaining) / self.total if self.total else 0
        self.visual_progress += (target - self.visual_progress) * 0.15
        self.area.queue_draw()
        return True

    def finish_period(self):
        self.running = False
        self.play.set_label("▶")

        if self.mode == "timer":
            self.remaining = 0
            self.visual_progress = 1.0
            notify(self.config, self.config["timer_title_custom"], self.config["timer_finished_message"])

            if self.config["timer_shutdown"]:
                self.schedule_shutdown()

            self.area.queue_draw()
            return

        if self.mode == "work":
            self.cycle_count += 1
            long_due = self.cycle_count % self.config["cycles_before_long_break"] == 0

            if long_due:
                self.mode = "long_break"
                minutes = self.config["long_break_minutes"]
                notify(self.config, "Long break", self.config["long_break_message"])
            else:
                self.mode = "short_break"
                minutes = self.config["short_break_minutes"]
                notify(self.config, "Short break", self.config["short_break_message"])

            self.running = self.config["auto_start_break"]
        else:
            self.mode = "work"
            minutes = self.config["work_minutes"]
            notify(self.config, self.config["timer_title"], self.config["work_message"])
            self.running = self.config["auto_start_work"]

        self.play.set_label("Ⅱ" if self.running else "▶")
        self.total = minutes * 60
        self.remaining = self.total
        self.visual_progress = 0.0
        self.last_tick = time.monotonic()
        self.area.queue_draw()

    def schedule_shutdown(self):
        delay = int(self.config["timer_shutdown_delay_seconds"])
        minutes = max(1, math.ceil(delay / 60))

        self.shutdown_scheduled = True
        self.shutdown_deadline = time.monotonic() + delay
        self.cancel_shutdown_btn.show()

        subprocess.Popen(["shutdown", "-h", f"+{minutes}"])
        notify(
            self.config,
            "Shutdown scheduled",
            f"System poweroff scheduled in about {minutes} minute(s). Press P× to cancel.",
        )

    def cancel_shutdown(self, *_):
        if self.shutdown_scheduled:
            subprocess.Popen(["shutdown", "-c"])
            notify(self.config, "Shutdown cancelled", "Scheduled system poweroff was cancelled.")

        self.shutdown_scheduled = False
        self.shutdown_deadline = None

        if hasattr(self, "cancel_shutdown_btn"):
            self.cancel_shutdown_btn.hide()

    def mode_label(self):
        if self.mode == "timer":
            return self.config["timer_title_custom"]
        if self.mode == "work":
            return self.config["timer_title"]
        if self.mode == "short_break":
            return "Short break"
        return "Long break"

    def draw_text(self, cr, text, size, y, color, weight=Pango.Weight.NORMAL):
        layout = PangoCairo.create_layout(cr)
        layout.set_text(text, -1)

        desc = Pango.FontDescription()
        desc.set_family("Sans")
        desc.set_size(size * Pango.SCALE)
        desc.set_weight(weight)
        layout.set_font_description(desc)

        w, _h = layout.get_pixel_size()
        alloc = self.area.get_allocation()
        cr.move_to((alloc.width - w) / 2, y)
        cr.set_source_rgb(*color)
        PangoCairo.show_layout(cr, layout)

    def draw(self, widget, cr):
        alloc = widget.get_allocation()
        w, h = alloc.width, alloc.height
        cx, cy = w / 2, h / 2
        r = min(w, h) * 0.38

        c = colors(self.config, self.mode)

        cr.set_source_rgb(*c["bg"])
        cr.paint()

        cr.set_line_width(4)
        cr.set_source_rgba(*c["track"])
        cr.arc(cx, cy, r, 0, 2 * math.pi)
        cr.stroke()

        progress = self.visual_progress if self.config["animations"] else (
            1 - max(0, self.remaining) / self.total if self.total else 0
        )

        cr.set_line_width(4)
        cr.set_line_cap(1)
        cr.set_source_rgb(*c["ring"])
        cr.arc(cx, cy, r, -math.pi / 2, -math.pi / 2 + progress * 2 * math.pi)
        cr.stroke()

        total_seconds = int(max(0, self.remaining))
        hours = total_seconds // 3600
        mins = (total_seconds % 3600) // 60
        secs = total_seconds % 60

        time_text = f"{hours:02d}:{mins:02d}:{secs:02d}" if hours > 0 else f"{mins:02d}:{secs:02d}"
        time_size = 28 if hours > 0 else 34

        if self.shutdown_scheduled and self.shutdown_deadline:
            left = max(0, int(self.shutdown_deadline - time.monotonic()))
            label = f"Poweroff in {left}s"
        else:
            label = self.mode_label()

        self.draw_text(cr, label, 12, h * 0.27, c["fg"], Pango.Weight.NORMAL)
        self.draw_text(cr, time_text, time_size, h * 0.43, c["fg"], Pango.Weight.LIGHT)

    def on_right_click(self, _widget, event):
        if event.button != 3:
            return False

        menu = Gtk.Menu()

        items = [
            ("Start / Pause", self.toggle),
            ("Reset current", self.reset_current),
            ("Reset Pomodoro", self.reset_pomodoro),
            ("Switch Pomodoro / Timer", self.toggle_timer_mode),
            ("Settings", self.open_settings),
        ]

        if self.shutdown_scheduled:
            items.append(("Cancel shutdown", self.cancel_shutdown))

        items.append(("Close", lambda *_: self.destroy()))

        for label, callback in items:
            item = Gtk.MenuItem(label=label)
            item.connect("activate", callback)
            menu.append(item)

        menu.show_all()
        menu.popup(None, None, None, None, event.button, event.time)
        return True
