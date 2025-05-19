import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib, Gio

from resources.resources_view import ResourcesTab
from process.process_view import ProcessesTab

class TaskManagerWindow(Gtk.ApplicationWindow):
    def __init__(self, app):
        Gtk.ApplicationWindow.__init__(self, application=app, title="Linux Task Manager")
        self.set_default_size(800, 600)
        self.maximize()

        # Enable dark mode by default
        settings = Gtk.Settings.get_default()
        settings.set_property("gtk-application-prefer-dark-theme", True)
        self.dark_mode = True

        # Header bar
        header = Gtk.HeaderBar()
        header.set_show_close_button(True)
        header.props.title = "Task Manager"
        self.set_titlebar(header)

        self.dark_mode_button = Gtk.Button()
        self.dark_mode_button.set_relief(Gtk.ReliefStyle.NONE)
        icon_name = "weather-clear-symbolic" if self.dark_mode else "weather-clear-night-symbolic"
        icon = Gtk.Image.new_from_icon_name(icon_name, Gtk.IconSize.BUTTON)
        self.dark_mode_button.set_image(icon)
        self.dark_mode_button.set_tooltip_text("Toggle Dark Mode")
        self.dark_mode_button.connect("clicked", self.on_dark_mode_toggle)
        header.pack_end(self.dark_mode_button)

        # Main layout
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.add(main_box)

        self.stack = Gtk.Stack()
        self.stack.set_transition_type(Gtk.StackTransitionType.CROSSFADE)
        self.stack.set_transition_duration(200)

        # Tabs
        resources_tab = ResourcesTab()
        processes_tab = ProcessesTab()

        self.stack.add_titled(resources_tab, "resources", "Resources")
        self.stack.add_titled(processes_tab, "processes", "Processes")

        # Tab switcher
        switcher_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        switcher_box.get_style_context().add_class("linked")
        switcher_box.set_halign(Gtk.Align.CENTER)
        switcher_box.set_margin_top(6)
        switcher_box.set_margin_bottom(6)

        self.buttons = []

        # Resources button
        resources_button = Gtk.ToggleButton()
        resources_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        resources_icon = Gtk.Image.new_from_icon_name("speedometer-symbolic", Gtk.IconSize.BUTTON)
        resources_label = Gtk.Label(label="Resources")
        resources_box.pack_start(resources_icon, False, False, 0)
        resources_box.pack_start(resources_label, False, False, 0)
        resources_button.add(resources_box)
        resources_button.connect("toggled", self.on_button_toggled, "resources")
        self.buttons.append(resources_button)
        switcher_box.pack_start(resources_button, False, False, 0)

        # Processes button
        processes_button = Gtk.ToggleButton()
        processes_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        processes_icon = Gtk.Image.new_from_icon_name("view-list-symbolic", Gtk.IconSize.BUTTON)
        processes_label = Gtk.Label(label="Processes")
        processes_box.pack_start(processes_icon, False, False, 0)
        processes_box.pack_start(processes_label, False, False, 0)
        processes_button.add(processes_box)
        processes_button.connect("toggled", self.on_button_toggled, "processes")
        self.buttons.append(processes_button)
        switcher_box.pack_start(processes_button, False, False, 0)

        # Add layout to window
        main_box.pack_start(switcher_box, False, False, 0)
        main_box.pack_start(Gtk.Separator(), False, False, 0)
        main_box.pack_start(self.stack, True, True, 0)

        self.stack.connect("notify::visible-child-name", self.on_stack_changed)

        # ✅ Set Processes tab after full GTK init
        GLib.idle_add(self.stack.set_visible_child_name, "processes")
        GLib.idle_add(processes_button.set_active, True)

    def on_dark_mode_toggle(self, button):
        settings = Gtk.Settings.get_default()
        self.dark_mode = not self.dark_mode
        settings.set_property("gtk-application-prefer-dark-theme", self.dark_mode)

        # ✅ Show icon that represents what theme will come next
        icon_name = "weather-clear-symbolic" if self.dark_mode else "weather-clear-night-symbolic"
        icon = Gtk.Image.new_from_icon_name(icon_name, Gtk.IconSize.BUTTON)
        button.set_image(icon)

    def on_button_toggled(self, button, name):
        if button.get_active():
            self.stack.set_visible_child_name(name)
            for btn in self.buttons:
                if btn != button:
                    btn.set_active(False)

    def on_stack_changed(self, stack, param):
        visible_child = stack.get_visible_child_name()
        for index, name in enumerate(["resources", "processes"]):
            self.buttons[index].set_active(visible_child == name)
