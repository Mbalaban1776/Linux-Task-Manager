import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib, Gio

from process.process_view import ProcessesTab
from resources.resources_view import ResourcesTab
from filesystems.filesystems_view import FileSystemsTab

class TaskManagerWindow(Gtk.ApplicationWindow):
    def __init__(self, app):
        Gtk.ApplicationWindow.__init__(self, application=app, title="Linux Task Manager")
        self.set_default_size(800, 600)
        
        # Create header bar
        header = Gtk.HeaderBar()
        header.set_show_close_button(True)
        header.props.title = "Task Manager"
        self.set_titlebar(header)
        
        # Add dark mode toggle button to header bar
        self.dark_mode_button = Gtk.Button()
        self.dark_mode_button.set_relief(Gtk.ReliefStyle.NONE)
        
        # Check current theme
        settings = Gtk.Settings.get_default()
        self.dark_mode = settings.get_property("gtk-application-prefer-dark-theme")
        
        # Set initial icon based on current theme
        icon_name = "weather-clear-night-symbolic" if self.dark_mode else "weather-clear-symbolic"
        icon = Gtk.Image.new_from_icon_name(icon_name, Gtk.IconSize.BUTTON)
        self.dark_mode_button.set_image(icon)
        self.dark_mode_button.set_tooltip_text("Toggle Dark Mode")
        self.dark_mode_button.connect("clicked", self.on_dark_mode_toggle)
        
        header.pack_end(self.dark_mode_button)
        
        # Main container
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.add(main_box)
        
        # Create stack for different views
        self.stack = Gtk.Stack()
        self.stack.set_transition_type(Gtk.StackTransitionType.CROSSFADE)
        self.stack.set_transition_duration(200)
        
        # Create tabs with icons
        resources_tab = ResourcesTab()
        processes_tab = ProcessesTab()
        filesystems_tab = FileSystemsTab()
        
        # Add tabs to stack
        self.stack.add_titled(resources_tab, "resources", "Resources")
        self.stack.add_titled(processes_tab, "processes", "Processes")
        self.stack.add_titled(filesystems_tab, "filesystems", "File Systems")
        
        # Create custom stack switcher with icons
        switcher_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        switcher_box.get_style_context().add_class("linked")
        
        # Style the switcher box
        switcher_box.set_halign(Gtk.Align.CENTER)
        switcher_box.set_margin_top(6)
        switcher_box.set_margin_bottom(6)
        
        # Create toggle buttons with icons
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
        
        # File Systems button
        filesystems_button = Gtk.ToggleButton()
        filesystems_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        filesystems_icon = Gtk.Image.new_from_icon_name("folder-symbolic", Gtk.IconSize.BUTTON)
        filesystems_label = Gtk.Label(label="File Systems")
        filesystems_box.pack_start(filesystems_icon, False, False, 0)
        filesystems_box.pack_start(filesystems_label, False, False, 0)
        filesystems_button.add(filesystems_box)
        filesystems_button.connect("toggled", self.on_button_toggled, "filesystems")
        self.buttons.append(filesystems_button)
        switcher_box.pack_start(filesystems_button, False, False, 0)
        
        # Set the first button as active
        resources_button.set_active(True)
        
        # Add switcher and stack to main box
        main_box.pack_start(switcher_box, False, False, 0)
        main_box.pack_start(Gtk.Separator(), False, False, 0)
        main_box.pack_start(self.stack, True, True, 0)
        
        # Connect stack property change to update button states
        self.stack.connect("notify::visible-child-name", self.on_stack_changed)
    
    def on_dark_mode_toggle(self, button):
        """Toggle between light and dark themes"""
        settings = Gtk.Settings.get_default()
        self.dark_mode = not self.dark_mode
        settings.set_property("gtk-application-prefer-dark-theme", self.dark_mode)
        
        # Update button icon
        icon_name = "weather-clear-night-symbolic" if self.dark_mode else "weather-clear-symbolic"
        icon = Gtk.Image.new_from_icon_name(icon_name, Gtk.IconSize.BUTTON)
        button.set_image(icon)
    
    def on_button_toggled(self, button, name):
        """Handle button toggle events"""
        if button.get_active():
            self.stack.set_visible_child_name(name)
            # Update other buttons
            for btn in self.buttons:
                if btn != button:
                    btn.set_active(False)
    
    def on_stack_changed(self, stack, param):
        """Handle stack changes to update button states"""
        visible_child = stack.get_visible_child_name()
        for button in self.buttons:
            # Simple way to get the page name from button
            if button == self.buttons[0] and visible_child == "resources":
                button.set_active(True)
            elif button == self.buttons[1] and visible_child == "processes":
                button.set_active(True)
            elif button == self.buttons[2] and visible_child == "filesystems":
                button.set_active(True)
            else:
                button.set_active(False)