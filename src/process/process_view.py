import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib, Gdk
import psutil
import os
import signal

class ProcessesTab(Gtk.Box):
    def __init__(self):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.set_margin_top(10)
        self.set_margin_bottom(10)
        self.set_margin_start(10)
        self.set_margin_end(10)
        
        # Create scrolled window for process list
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        self.pack_start(scrolled_window, True, True, 0)
        
        # Create the tree view model
        self.process_store = Gtk.ListStore(str, int, float, str, str, str)
        
        # Create the tree view
        self.process_view = Gtk.TreeView(model=self.process_store)
        self.process_view.set_rules_hint(True)  # Alternating row colors
        
        # Add selection handling
        self.selection = self.process_view.get_selection()
        self.selection.connect("changed", self.on_process_selected)
        
        # Create columns
        columns = [
            ("Name", 0, 250),
            ("ID", 1, 70),
            ("CPU %", 2, 80),
            ("Memory", 3, 100),
            ("Disk Read", 4, 100),
            ("Disk Write", 5, 100)
        ]
        
        for title, col_id, width in columns:
            renderer = Gtk.CellRendererText()
            column = Gtk.TreeViewColumn(title, renderer, text=col_id)
            column.set_sort_column_id(col_id)
            column.set_resizable(True)
            column.set_min_width(width)
            
            # Right-align numeric columns
            if col_id in [1, 2]:
                renderer.set_alignment(1.0, 0.5)  # Right alignment
                column.set_alignment(1.0)
            
            self.process_view.append_column(column)
        
        scrolled_window.add(self.process_view)
        
        # Control buttons area
        controls_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self.pack_start(controls_box, False, False, 0)
        
        # End Process button
        self.end_process_button = Gtk.Button(label="End Process")
        self.end_process_button.connect("clicked", self.on_end_process_clicked)
        self.end_process_button.set_sensitive(False)  # Disabled until selection
        controls_box.pack_start(self.end_process_button, False, False, 0)
        
        # Spacing
        controls_box.pack_start(Gtk.Label(""), True, True, 0)
        
        # Refresh rate control
        rate_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        rate_label = Gtk.Label(label="Refresh rate:")
        
        self.refresh_combo = Gtk.ComboBoxText()
        for rate in ["1 second", "2 seconds", "3 seconds", "5 seconds"]:
            self.refresh_combo.append_text(rate)
        self.refresh_combo.set_active(1)  # Default to 2 seconds
        self.refresh_combo.connect("changed", self.on_refresh_rate_changed)
        
        rate_box.pack_start(rate_label, False, False, 0)
        rate_box.pack_start(self.refresh_combo, False, False, 0)
        controls_box.pack_end(rate_box, False, False, 0)
        
        # Track process IO data between updates
        self.process_io = {}
        
        # Start timer (default 2 seconds)
        self.update_timeout_id = GLib.timeout_add(2000, self.update_process_list)
        
        # Initial update
        self.update_process_list()
    
    def update_process_list(self):
        """Update the process list with current data"""
        # Remember selection if it exists
        selected_pid = None
        if self.selection.get_selected()[1] is not None:
            model, iter = self.selection.get_selected()
            selected_pid = model.get_value(iter, 1)
        
        # Clear the current list
        self.process_store.clear()
        
        # Get all processes
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info']):
            try:
                processes.append(proc)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        
        # Get CPU percentages (first call returns 0, need to call again after delay)
        # We'll use the cached values from previous calls
        
        # Process each process
        for proc in processes:
            try:
                pid = proc.pid
                name = proc.name()
                
                # Get CPU and memory info
                cpu_percent = proc.cpu_percent(interval=None)  # Non-blocking
                mem_info = proc.memory_info()
                memory_str = f"{mem_info.rss / (1024 * 1024):.1f} MB"
                
                # Get disk I/O if available
                disk_read = "—"
                disk_write = "—"
                
                try:
                    io_counters = proc.io_counters()
                    
                    # Calculate read/write rates if we have previous values
                    if pid in self.process_io:
                        last_time, last_read, last_write = self.process_io[pid]
                        
                        time_delta = GLib.get_monotonic_time() / 1000000 - last_time
                        if time_delta > 0:
                            read_rate = (io_counters.read_bytes - last_read) / time_delta
                            write_rate = (io_counters.write_bytes - last_write) / time_delta
                            
                            if read_rate > 0:
                                disk_read = self.format_bytes_rate(read_rate)
                            if write_rate > 0:  
                                disk_write = self.format_bytes_rate(write_rate)
                    
                    # Store current values for next calculation
                    current_time = GLib.get_monotonic_time() / 1000000  # Seconds
                    self.process_io[pid] = (current_time, io_counters.read_bytes, io_counters.write_bytes)
                
                except (psutil.AccessDenied, AttributeError):
                    # Some processes don't allow IO monitoring or don't have IO counters
                    pass
                
                # Add to the store
                self.process_store.append([name, pid, cpu_percent, memory_str, disk_read, disk_write])
                
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                # Process might have terminated while we were iterating
                pass
        
        # Sort by CPU usage (descending)
        self.process_store.set_sort_column_id(2, Gtk.SortType.DESCENDING)
        
        # Restore selection if possible
        if selected_pid is not None:
            iter = self.process_store.get_iter_first()
            while iter:
                pid = self.process_store.get_value(iter, 1)
                if pid == selected_pid:
                    self.selection.select_iter(iter)
                    break
                iter = self.process_store.iter_next(iter)
        
        # Continue the timer
        return True
    
    def on_process_selected(self, selection):
        """Enable the End Process button when a process is selected"""
        model, iter = selection.get_selected()
        self.end_process_button.set_sensitive(iter is not None)
    
    def on_end_process_clicked(self, button):
        """End the selected process"""
        model, iter = self.selection.get_selected()
        if iter is not None:
            pid = model.get_value(iter, 1)
            try:
                # Try SIGTERM first
                os.kill(pid, signal.SIGTERM)
                # Force update after a short delay
                GLib.timeout_add(500, self.update_process_list)
            except ProcessLookupError:
                # Process already gone
                self.update_process_list()
            except PermissionError:
                dialog = Gtk.MessageDialog(
                    transient_for=self.get_toplevel(),
                    message_type=Gtk.MessageType.ERROR,
                    buttons=Gtk.ButtonsType.OK,
                    text="Permission Denied"
                )
                dialog.format_secondary_text("You don't have permission to end this process.")
                dialog.run()
                dialog.destroy()
    
    def on_refresh_rate_changed(self, combo):
        """Change the refresh rate based on combo selection"""
        text = combo.get_active_text()
        if text:
            # Parse seconds from text (e.g., "2 seconds" -> 2)
            seconds = int(text.split()[0])
            
            # Remove existing timer
            if hasattr(self, 'update_timeout_id'):
                GLib.source_remove(self.update_timeout_id)
            
            # Create new timer
            self.update_timeout_id = GLib.timeout_add(seconds * 1000, self.update_process_list)
    
    def format_bytes_rate(self, bytes_per_sec):
        """Format bytes per second to human-readable format"""
        if bytes_per_sec < 1024:
            return f"{bytes_per_sec:.0f} B/s"
        elif bytes_per_sec < 1024**2:
            return f"{bytes_per_sec/1024:.1f} KB/s"
        elif bytes_per_sec < 1024**3:
            return f"{bytes_per_sec/(1024**2):.1f} MB/s"
        else:
            return f"{bytes_per_sec/(1024**3):.1f} GB/s"