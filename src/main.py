#!/usr/bin/env python3

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib

from ui.app_window import TaskManagerWindow

def main():
    # Initialize the application
    app = Gtk.Application(application_id="com.github.Mbalaban1776.Linux-Task-Manager")
    GLib.set_application_name("Linux Task Manager")
    
    def on_activate(app):
        # Create the main window when the app activates
        win = TaskManagerWindow(app)
        win.show_all()
    
    app.connect("activate", on_activate)
    app.run(None)

if __name__ == "__main__":
    main()