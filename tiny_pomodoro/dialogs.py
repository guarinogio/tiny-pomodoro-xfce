import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk


class StyledDialog(Gtk.Dialog):
    def apply_dialog_css(self):
        css = b"""
        dialog { background: #2f2f2f; }
        dialog label, dialog checkbutton { color: #f2f2f2; font-size: 13px; }
        dialog entry, dialog spinbutton, dialog spinbutton entry,
        dialog combobox, dialog combobox button {
            color: #f7f7f7;
            background: #252525;
            border-radius: 6px;
            border: 1px solid #4d4d4d;
            min-height: 28px;
        }
        dialog button {
            color: #f7f7f7;
            background: #454545;
            border: 1px solid #666;
            border-radius: 8px;
            padding: 7px 14px;
            text-shadow: none;
            box-shadow: none;
        }
        dialog button:hover { background: #555; }
        dialog button.suggested-action {
            background: #2d72d9;
            border-color: #3d82e9;
            color: white;
        }
        .danger { color: #ffb4b4; font-weight: 600; }
        """
        provider = Gtk.CssProvider()
        provider.load_from_data(css)
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
        )

    def attach_rows(self, grid, rows):
        for i, (label, widget) in enumerate(rows):
            grid.attach(Gtk.Label(label=label, xalign=0), 0, i, 1, 1)
            grid.attach(widget, 1, i, 1, 1)

    def add_common(self, parent):
        self.size = Gtk.SpinButton.new_with_range(160, 360, 10)
        self.size.set_value(parent.config["size"])

        self.opacity = Gtk.SpinButton.new_with_range(0.45, 1.0, 0.05)
        self.opacity.set_digits(2)
        self.opacity.set_value(parent.config["opacity"])

        self.inactive_opacity = Gtk.SpinButton.new_with_range(0.30, 1.0, 0.05)
        self.inactive_opacity.set_digits(2)
        self.inactive_opacity.set_value(parent.config["inactive_opacity"])

        self.theme = Gtk.ComboBoxText()
        self.theme.append("system", "System")
        self.theme.append("light", "Light")
        self.theme.append("dark", "Dark")
        self.theme.set_active_id(parent.config["theme"])

        self.top = Gtk.CheckButton(label="Always on top")
        self.top.set_active(parent.config["always_on_top"])

        self.notify = Gtk.CheckButton(label="System notifications")
        self.notify.set_active(parent.config["notify"])

        self.sound = Gtk.CheckButton(label="Sound")
        self.sound.set_active(parent.config["sound"])

        self.sound_file = Gtk.Entry()
        self.sound_file.set_placeholder_text("Optional custom sound file")
        self.sound_file.set_text(parent.config["sound_file"])

        self.animations = Gtk.CheckButton(label="Animations")
        self.animations.set_active(parent.config["animations"])

        self.dim_when_inactive = Gtk.CheckButton(label="Dim when inactive")
        self.dim_when_inactive.set_active(parent.config["dim_when_inactive"])

        self.compact_mode = Gtk.CheckButton(label="Compact mode")
        self.compact_mode.set_active(parent.config["compact_mode"])

        self.autostart = Gtk.CheckButton(label="Start with session")
        self.autostart.set_active(parent.config["autostart"])

    def attach_common(self, grid, start):
        common_rows = [
            ("Window size", self.size),
            ("Opacity", self.opacity),
            ("Inactive opacity", self.inactive_opacity),
            ("Theme", self.theme),
            ("Custom sound file", self.sound_file),
        ]

        for offset, (label, widget) in enumerate(common_rows):
            grid.attach(Gtk.Label(label=label, xalign=0), 0, start + offset, 1, 1)
            grid.attach(widget, 1, start + offset, 1, 1)

        i = start + len(common_rows)
        grid.attach(self.top, 0, i, 2, 1)
        grid.attach(self.notify, 0, i + 1, 2, 1)
        grid.attach(self.sound, 0, i + 2, 2, 1)
        grid.attach(self.animations, 0, i + 3, 2, 1)
        grid.attach(self.dim_when_inactive, 0, i + 4, 2, 1)
        grid.attach(self.compact_mode, 0, i + 5, 2, 1)
        grid.attach(self.autostart, 0, i + 6, 2, 1)

    def common_values(self):
        return {
            "size": self.size.get_value_as_int(),
            "opacity": self.opacity.get_value(),
            "inactive_opacity": self.inactive_opacity.get_value(),
            "theme": self.theme.get_active_id() or "system",
            "always_on_top": self.top.get_active(),
            "notify": self.notify.get_active(),
            "sound": self.sound.get_active(),
            "sound_file": self.sound_file.get_text().strip(),
            "animations": self.animations.get_active(),
            "dim_when_inactive": self.dim_when_inactive.get_active(),
            "compact_mode": self.compact_mode.get_active(),
            "autostart": self.autostart.get_active(),
        }

    def finish_dialog(self):
        self.add_button("Cancel", Gtk.ResponseType.CANCEL)
        save = self.add_button("Save", Gtk.ResponseType.OK)
        save.get_style_context().add_class("suggested-action")
        self.apply_dialog_css()
        self.show_all()


class PomodoroSettingsDialog(StyledDialog):
    def __init__(self, parent):
        super().__init__(title="Pomodoro Settings", transient_for=parent, modal=True)
        self.set_resizable(False)
        self.set_border_width(14)

        grid = Gtk.Grid(column_spacing=14, row_spacing=10)
        self.get_content_area().add(grid)

        self.title_entry = Gtk.Entry()
        self.title_entry.set_text(parent.config["timer_title"])

        self.work = Gtk.SpinButton.new_with_range(1, 180, 1)
        self.work.set_value(parent.config["work_minutes"])

        self.short_break = Gtk.SpinButton.new_with_range(1, 60, 1)
        self.short_break.set_value(parent.config["short_break_minutes"])

        self.long_break = Gtk.SpinButton.new_with_range(1, 120, 1)
        self.long_break.set_value(parent.config["long_break_minutes"])

        self.cycles = Gtk.SpinButton.new_with_range(1, 12, 1)
        self.cycles.set_value(parent.config["cycles_before_long_break"])

        self.short_msg = Gtk.Entry()
        self.short_msg.set_text(parent.config["short_break_message"])

        self.long_msg = Gtk.Entry()
        self.long_msg.set_text(parent.config["long_break_message"])

        self.work_msg = Gtk.Entry()
        self.work_msg.set_text(parent.config["work_message"])

        self.auto_start_break = Gtk.CheckButton(label="Auto-start breaks after focus")
        self.auto_start_break.set_active(parent.config["auto_start_break"])

        self.auto_start_work = Gtk.CheckButton(label="Auto-start work after breaks")
        self.auto_start_work.set_active(parent.config["auto_start_work"])

        self.add_common(parent)

        rows = [
            ("Timer title", self.title_entry),
            ("Work minutes", self.work),
            ("Short break minutes", self.short_break),
            ("Long break minutes", self.long_break),
            ("Cycles before long break", self.cycles),
            ("Short break message", self.short_msg),
            ("Long break message", self.long_msg),
            ("Work message", self.work_msg),
        ]

        self.attach_rows(grid, rows)
        start = len(rows)
        grid.attach(self.auto_start_break, 0, start, 2, 1)
        grid.attach(self.auto_start_work, 0, start + 1, 2, 1)
        self.attach_common(grid, start + 2)
        self.finish_dialog()

    def get_values(self):
        values = self.common_values()
        values.update({
            "timer_title": self.title_entry.get_text().strip() or "Pomodoro",
            "work_minutes": self.work.get_value_as_int(),
            "short_break_minutes": self.short_break.get_value_as_int(),
            "long_break_minutes": self.long_break.get_value_as_int(),
            "cycles_before_long_break": self.cycles.get_value_as_int(),
            "short_break_message": self.short_msg.get_text().strip(),
            "long_break_message": self.long_msg.get_text().strip(),
            "work_message": self.work_msg.get_text().strip(),
            "auto_start_break": self.auto_start_break.get_active(),
            "auto_start_work": self.auto_start_work.get_active(),
        })
        return values


class TimerSettingsDialog(StyledDialog):
    def __init__(self, parent):
        super().__init__(title="Timer Settings", transient_for=parent, modal=True)
        self.set_resizable(False)
        self.set_border_width(14)

        grid = Gtk.Grid(column_spacing=14, row_spacing=10)
        self.get_content_area().add(grid)

        self.timer_title_custom = Gtk.Entry()
        self.timer_title_custom.set_text(parent.config["timer_title_custom"])

        self.hours = Gtk.SpinButton.new_with_range(0, 24, 1)
        self.hours.set_value(parent.config["timer_hours"])

        self.minutes = Gtk.SpinButton.new_with_range(0, 300, 1)
        self.minutes.set_value(parent.config["timer_minutes"])

        self.seconds = Gtk.SpinButton.new_with_range(0, 59, 1)
        self.seconds.set_value(parent.config["timer_seconds"])

        self.finished_msg = Gtk.Entry()
        self.finished_msg.set_text(parent.config["timer_finished_message"])

        self.shutdown = Gtk.CheckButton(label="Shutdown system when timer finishes")
        self.shutdown.set_active(parent.config["timer_shutdown"])

        self.shutdown_confirm = Gtk.CheckButton(label="I understand this can power off my computer")
        self.shutdown_confirm.set_active(parent.config["timer_shutdown"])

        self.shutdown_delay = Gtk.SpinButton.new_with_range(10, 600, 10)
        self.shutdown_delay.set_value(parent.config["timer_shutdown_delay_seconds"])

        warning = Gtk.Label(
            label="Warning: shutdown schedules a system poweroff. You can cancel it from the app before it runs.",
            xalign=0,
        )
        warning.get_style_context().add_class("danger")
        warning.set_line_wrap(True)

        self.add_common(parent)

        rows = [
            ("Timer title", self.timer_title_custom),
            ("Hours", self.hours),
            ("Minutes", self.minutes),
            ("Seconds", self.seconds),
            ("Finished message", self.finished_msg),
            ("Shutdown delay seconds", self.shutdown_delay),
        ]

        self.attach_rows(grid, rows)
        start = len(rows)
        grid.attach(self.shutdown, 0, start, 2, 1)
        grid.attach(self.shutdown_confirm, 0, start + 1, 2, 1)
        grid.attach(warning, 0, start + 2, 2, 1)
        self.attach_common(grid, start + 3)
        self.finish_dialog()

    def get_values(self):
        hours = self.hours.get_value_as_int()
        minutes = self.minutes.get_value_as_int()
        seconds = self.seconds.get_value_as_int()

        if hours == 0 and minutes == 0 and seconds == 0:
            minutes = 1

        values = self.common_values()
        values.update({
            "timer_title_custom": self.timer_title_custom.get_text().strip() or "Timer",
            "timer_hours": hours,
            "timer_minutes": minutes,
            "timer_seconds": seconds,
            "timer_finished_message": self.finished_msg.get_text().strip(),
            "timer_shutdown": self.shutdown.get_active() and self.shutdown_confirm.get_active(),
            "timer_shutdown_delay_seconds": self.shutdown_delay.get_value_as_int(),
        })
        return values
