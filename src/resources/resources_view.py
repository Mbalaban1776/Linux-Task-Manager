import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

class ResourcesTab(Gtk.Box):
    def __init__(self):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL, spacing=6)
        
        # Placeholder label
        label = Gtk.Label(label="Resources tab - Content coming soon")
        self.pack_start(label, True, True, 0)