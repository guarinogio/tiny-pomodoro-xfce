import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from .window import PomodoroWindow


def main(app_path):
    win = PomodoroWindow(app_path)
    win.connect("destroy", Gtk.main_quit)
    Gtk.main()
