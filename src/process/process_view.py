import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib, Gdk
import psutil
import os
import signal
import time

class ProcessesTab(Gtk.Box):
    def __init__(self):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.set_margin_top(10)
        self.set_margin_bottom(10)
        self.set_margin_start(10)
        self.set_margin_end(10)
        
        # Create scrolled window for process list
        self.scrolled_window = Gtk.ScrolledWindow()
        self.scrolled_window.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        self.pack_start(self.scrolled_window, True, True, 0)
        
        # Create the tree view model - columns: name, memory_mb, cpu%, memory_str, pid
        self.process_store = Gtk.ListStore(str, float, str, str, int)
        
        # Create the tree view
        self.process_view = Gtk.TreeView(model=self.process_store)
        self.process_view.set_rules_hint(True)  # Alternating row colors
        
        # Add selection handling
        self.selection = self.process_view.get_selection()
        self.selection.connect("changed", self.on_process_selected)
        
        # Create columns
        self.columns_info = [
            ("Name", 0, 0.40),    # 40% width
            ("PID", 4, 0.20),     # 20% width
            ("CPU %", 2, 0.20),   # 20% width
            ("Memory", 3, 0.20)   # 20% width
        ]
        
        self.columns = []
        for i, (title, col_id, width_ratio) in enumerate(self.columns_info):
            renderer = Gtk.CellRendererText()
            if title == "Name":
                renderer.set_property("ellipsize", 3)  # PANGO_ELLIPSIZE_END
            
            column = Gtk.TreeViewColumn(title, renderer, text=col_id)
            
            # Set sorting
            if title == "Memory":
                column.set_sort_column_id(1)  # Sort by the numeric memory value
            else:
                column.set_sort_column_id(col_id)
            
            # Make columns resizable
            column.set_resizable(True)
            
            # Right-align numeric columns including Memory
            if title in ["PID", "CPU %", "Memory"]:
                renderer.set_alignment(1.0, 0.5)
                column.set_alignment(1.0)
            
            # Set sizing properties
            if title == "Name":
                column.set_expand(True)
                column.set_min_width(100)
            else:
                column.set_expand(False)
                column.set_min_width(50)
            
            self.process_view.append_column(column)
            self.columns.append(column)
        
        self.scrolled_window.add(self.process_view)
        
        # Control buttons area
        controls_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self.pack_start(controls_box, False, False, 0)
        
        # End Process button
        self.end_process_button = Gtk.Button(label="End Process")
        self.end_process_button.connect("clicked", self.on_end_process_clicked)
        self.end_process_button.set_sensitive(False)  # Disabled until selection
        
        # Add CSS class for styling
        self.end_process_button.get_style_context().add_class("end-process-button")
        
        # Add custom CSS for the button
        css_provider = Gtk.CssProvider()
        css_provider.load_from_data(b"""
        .end-process-button:disabled {
            opacity: 0.5;
        }
        .end-process-button {
            background-color: #ed333b;
            background-image: none;
            color: white;
            border: 1px solid #c01c28;
            text-shadow: none;
            box-shadow: none;
        }
        .end-process-button:hover {
            background-color: #f03939;
            background-image: none;
            color: white;
            border-color: #ed333b;
        }
        .end-process-button:active {
            background-color: #c01c28;
            background-image: none;
            color: white;
            border-color: #a51d2d;
        }
        .end-process-button label {
            color: white;
        }
        """)
        
        # Apply CSS to the screen
        screen = Gdk.Screen.get_default()
        style_context = Gtk.StyleContext()
        style_context.add_provider_for_screen(screen, css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        
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
        
        # Initialize CPU percent tracking
        self.initialize_cpu_tracking()
        
        # Start timer (default 2 seconds)
        self.update_timeout_id = GLib.timeout_add(2000, self.update_process_list)
        
        # Initial update
        self.update_process_list()
        
        # Sort by memory usage by default (descending)
        self.process_store.set_sort_column_id(1, Gtk.SortType.DESCENDING)
        
        # Connect to configure event to handle resizing
        self.scrolled_window.connect("size-allocate", self.on_window_resize)
        
        # Set initial column widths after widget is realized
        self.process_view.connect("realize", self.set_initial_column_widths)
    
    def set_initial_column_widths(self, widget):
        """Set initial column widths based on window size"""
        GLib.idle_add(self.update_column_widths)
    
    def on_window_resize(self, widget, allocation):
        """Handle window resize to adjust column widths"""
        GLib.idle_add(self.update_column_widths)
    
    def update_column_widths(self):
        """Update column widths based on current window size"""
        # Get the available width
        allocation = self.scrolled_window.get_allocation()
        available_width = allocation.width
        
        # Account for scrollbar if visible
        vscrollbar = self.scrolled_window.get_vscrollbar()
        if vscrollbar and vscrollbar.get_visible():
            scrollbar_width = vscrollbar.get_allocated_width()
            available_width -= scrollbar_width
        
        # Subtract some padding for borders
        available_width -= 10
        
        if available_width > 400:  # Only apply proportional widths if enough space
            # Calculate proportional widths
            name_width = int(available_width * 0.40)
            other_width = int(available_width * 0.20)
            
            # Set column widths
            self.columns[0].set_fixed_width(name_width)  # Name
            self.columns[1].set_fixed_width(other_width)  # PID
            self.columns[2].set_fixed_width(other_width)  # CPU %
            self.columns[3].set_fixed_width(other_width)  # Memory
            
            # Set sizing to fixed
            for column in self.columns:
                column.set_sizing(Gtk.TreeViewColumnSizing.FIXED)
        else:
            # For small windows, use automatic sizing
            for column in self.columns:
                column.set_sizing(Gtk.TreeViewColumnSizing.GROW_ONLY)
        
        return False
    
    def initialize_cpu_tracking(self):
        """Initialize CPU tracking for all processes"""
        for proc in psutil.process_iter(['pid']):
            try:
                proc.cpu_percent(interval=None)  # First call to start tracking
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
    
    def update_process_list(self):
        """Update the process list with current data"""
        # Save current scroll position
        vadj = self.scrolled_window.get_vadjustment()
        hadj = self.scrolled_window.get_hadjustment()
        vscroll_position = vadj.get_value()
        hscroll_position = hadj.get_value()
        
        # Remember selection if it exists
        selected_pid = None
        if self.selection.get_selected()[1] is not None:
            model, iter = self.selection.get_selected()
            selected_pid = model.get_value(iter, 4)  # PID is now in column 4
        
        # Clear the current list
        self.process_store.clear()
        
        # Get all processes
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'memory_info']):
            try:
                processes.append(proc)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        
        # Process each process
        for proc in processes:
            try:
                pid = proc.pid
                name = proc.name()
                
                # Get CPU percentage
                try:
                    cpu_percent = proc.cpu_percent(interval=None)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    cpu_percent = 0.0
                
                # Format CPU percentage with one decimal place
                cpu_percent_str = f"{cpu_percent:.1f}"
                
                # Get memory info
                mem_info = proc.memory_info()
                memory_mb = mem_info.rss / (1024 * 1024)  # Convert to MB
                memory_str = f"{memory_mb:.1f} MB"
                
                # Add to the store
                self.process_store.append([name, memory_mb, cpu_percent_str, memory_str, pid])
                
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                # Process might have terminated while we were iterating
                pass
        
        # Restore selection if possible
        if selected_pid is not None:
            iter = self.process_store.get_iter_first()
            while iter:
                pid = self.process_store.get_value(iter, 4)
                if pid == selected_pid:
                    self.selection.select_iter(iter)
                    break
                iter = self.process_store.iter_next(iter)
        
        # Restore scroll position
        def restore_scroll():
            vadj.set_value(vscroll_position)
            hadj.set_value(hscroll_position)
            return False
        
        # Restore scroll position after the view has been updated
        GLib.idle_add(restore_scroll)
        
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
            pid = model.get_value(iter, 4)  # PID is in column 4
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