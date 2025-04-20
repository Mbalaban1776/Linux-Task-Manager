import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib

from process.process_view import ProcessesTab
from resources.resources_view import ResourcesTab
from filesystems.filesystems_view import FileSystemsTab

class TaskManagerWindow(Gtk.ApplicationWindow):
    def __init__(self, app):
        Gtk.ApplicationWindow.__init__(self, application=app, title="Linux Task Manager")
        self.set_default_size(800, 600)
        
        # Create header bar with tabs
        header = Gtk.HeaderBar()
        header.set_show_close_button(True)
        header.props.title = "Task Manager"
        self.set_titlebar(header)
        
        # Main stack for different views/tabs
        self.stack = Gtk.Stack()
        self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
        self.stack.set_transition_duration(200)
        
        # Stack switcher (tabs)
        stack_switcher = Gtk.StackSwitcher()
        stack_switcher.set_stack(self.stack)
        header.set_custom_title(stack_switcher)
        
        # Create tabs
        resources_tab = ResourcesTab()
        processes_tab = ProcessesTab()
        filesystems_tab = FileSystemsTab()
        
        # Add tabs to stack
        self.stack.add_titled(resources_tab, "resources", "Resources")
        self.stack.add_titled(processes_tab, "processes", "Processes")
        self.stack.add_titled(filesystems_tab, "filesystems", "File Systems")
        
        # Main container
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        main_box.pack_start(self.stack, True, True, 0)
        self.add(main_box)