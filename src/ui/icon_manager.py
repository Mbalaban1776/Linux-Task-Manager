import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

class IconManager:
    def __init__(self):
        self.icon_theme = Gtk.IconTheme.get_default()
        self.icon_cache = {}
        # Mapping process names (or parts) to known icon names
        self.manual_mappings = {
            "chrome": "google-chrome",
            "firefox-bin": "firefox",
            "code": "visual-studio-code",
            "nautilus": "org.gnome.Nautilus",
            "gnome-calendar": "org.gnome.Calendar",
            "gnome-software": "org.gnome.Software",
            "gnome-system-monitor": "org.gnome.SystemMonitor",
            "gnome-shell": "gnome-shell",
            "xwayland": "xorg",
            "systemd": "system-run",
            "gjs": "application-javascript",
        }

    def get_icon_for_process(self, process_name):
        process_name = process_name.lower()
        if process_name in self.icon_cache:
            return self.icon_cache[process_name]

        # 1. Check manual mapping for the full name
        if process_name in self.manual_mappings:
            icon_name = self.manual_mappings[process_name]
            if self.icon_theme.has_icon(icon_name):
                self.icon_cache[process_name] = icon_name
                return icon_name

        # 2. Check for exact match
        if self.icon_theme.has_icon(process_name):
            self.icon_cache[process_name] = process_name
            return process_name

        # 3. Try splitting the name and check parts against the icon theme
        parts = process_name.split('-')
        if len(parts) > 1:
            # Check for parts as icons directly, prefer longer, more specific parts
            for part in reversed(parts):
                 if len(part) > 3 and self.icon_theme.has_icon(part):
                    self.icon_cache[process_name] = part
                    return part

        # 4. Generic fallback for system daemons
        if "daemon" in process_name or "service" in process_name or "gdm" in process_name:
            self.icon_cache[process_name] = "system-run"
            return "system-run"

        # 5. Final fallback
        self.icon_cache[process_name] = "application-x-executable"
        return "application-x-executable" 