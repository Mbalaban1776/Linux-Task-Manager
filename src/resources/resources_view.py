# src/resources/resources_view.py

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib, Pango
import cairo
from . import cpu_info
from . import memory_info

HISTORY_LENGTH = 60

class DetailsGrid(Gtk.Grid):
    def __init__(self, static_info, dynamic_info_func):
        super().__init__()
        self.dynamic_info_func = dynamic_info_func
        self.set_column_spacing(20)
        self.set_row_spacing(10)

        self.dynamic_labels = {}
        row = 0
        col = 0
        
        # Dynamic info on the left
        for key, value in self.dynamic_info_func().items():
            label_key = Gtk.Label(label=key)
            label_key.set_halign(Gtk.Align.START)
            
            label_value = Gtk.Label(label=value)
            label_value.set_halign(Gtk.Align.START)
            label_value.get_style_context().add_class("dim-label") # Make value stand out
            
            self.attach(label_key, col, row, 1, 1)
            self.attach(label_value, col + 1, row, 1, 1)
            self.dynamic_labels[key] = label_value
            row += 1
            if row > 1: # two rows for dynamic info
                row = 0
                col += 2

        # Static info on the right
        col = 4 # Start static info in a new column
        row = 0
        for key, value in static_info.items():
            label_key = Gtk.Label(label=f"{key}:")
            label_key.set_halign(Gtk.Align.END)

            label_value = Gtk.Label(label=value)
            label_value.set_halign(Gtk.Align.START)

            self.attach(label_key, col, row, 1, 1)
            self.attach(label_value, col + 1, row, 1, 1)
            row += 1

    def update(self):
        for key, value in self.dynamic_info_func().items():
            self.dynamic_labels[key].set_text(value)

class CPUHistoryGraph(Gtk.DrawingArea):
    def __init__(self, data_func):
        super().__init__()
        self.data_func = data_func
        self.data = [0.0] * HISTORY_LENGTH
        self.set_size_request(800, 200)
        self.connect("draw", self.on_draw)

    def update(self):
        self.data.pop(0)
        self.data.append(self.data_func())
        self.queue_draw()
        return True

    def on_draw(self, widget, cr):
        width = widget.get_allocated_width()
        height = widget.get_allocated_height()

        label_padding = 40
        graph_width = width - label_padding

        # Background
        cr.set_source_rgb(1, 1, 1)  # White
        cr.paint()

        # Grid lines and labels
        cr.set_source_rgba(0, 0, 0, 0.1)
        cr.set_line_width(1)

        # Horizontal grid lines
        for i in range(1, 5):  # 20, 40, 60, 80% lines
            y = i * height / 5
            cr.move_to(0, y)
            cr.line_to(graph_width, y)
        cr.stroke()

        # Vertical grid lines
        cr.set_source_rgba(0, 0, 0, 0.1)
        for i in range(1, 10):
            cr.move_to(i * graph_width / 10, 0)
            cr.line_to(i * graph_width / 10, height)
        cr.stroke()
        
        # Y-axis labels
        cr.set_source_rgba(0, 0, 0, 0.7)  # Text color
        cr.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        cr.set_font_size(12)

        for i in range(6):  # 0, 20, 40, 60, 80, 100
            percentage = 100 - i * 20
            text = f"{percentage}%"
            y = i * height / 5

            (x_bearing, y_bearing, text_width, text_height, x_advance, y_advance) = cr.text_extents(text)

            text_y = y
            if i == 0:  # 100%
                text_y = y + text_height + 2  # Position below top line
            elif i == 5:  # 0%
                text_y = y - 2  # Position above bottom line
            else:
                text_y = y + text_height / 2

            cr.move_to(graph_width + 5, text_y)
            cr.show_text(text)

        # Graph line
        cr.set_source_rgb(0.2, 0.6, 0.9)
        cr.set_line_width(2)
        step = graph_width / (HISTORY_LENGTH - 1)

        if not self.data:
            return

        cr.move_to(0, height - (self.data[0] / 100) * height)
        for i in range(1, len(self.data)):
            x = i * step
            y = height - (self.data[i] / 100) * height
            cr.line_to(x, y)
        cr.stroke()

class CPUView(Gtk.Box):
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=15)
        self.set_border_width(10)
        
        # Title
        title_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        cpu_label = Gtk.Label(label="CPU")
        cpu_label.get_style_context().add_class("title-1")
        
        cpu_name_label = Gtk.Label(label=cpu_info.get_cpu_name())
        cpu_name_label.set_halign(Gtk.Align.END)
        
        title_box.pack_start(cpu_label, False, False, 0)
        title_box.pack_start(cpu_name_label, True, True, 0)
        self.pack_start(title_box, False, False, 0)

        # Graph
        self.graph = CPUHistoryGraph(cpu_info.get_cpu_percent)
        self.pack_start(self.graph, True, True, 0)

        # Details
        static_info = cpu_info.get_static_cpu_info()
        self.details_grid = DetailsGrid(static_info, cpu_info.get_dynamic_cpu_info)
        self.pack_start(self.details_grid, False, False, 0)

        GLib.timeout_add(1000, self.update)
    
    def update(self):
        cpu_info.update_dynamic_info()
        self.graph.update()
        self.details_grid.update()
        return True

class MemoryHistoryGraph(CPUHistoryGraph):
    def __init__(self):
        super().__init__(memory_info.get_memory_percent)

class MemoryCompositionBar(Gtk.DrawingArea):
    def __init__(self):
        super().__init__()
        self.set_size_request(-1, 25)
        self.connect("draw", self.on_draw)

    def on_draw(self, widget, cr):
        width = widget.get_allocated_width()
        height = widget.get_allocated_height()

        composition = memory_info.get_memory_composition()
        total = composition.get("composition_total", 1)
        if total == 0: return

        colors = {
            "used": (0.5, 0.5, 0.8),
            "cached": (0.2, 0.6, 0.9),
            "buffers": (0.6, 0.8, 1.0),
            "free": (0.9, 0.9, 0.9),
        }
        
        current_x = 0
        for part in ["used", "cached", "buffers", "free"]:
            key = f"composition_{part}"
            value = composition.get(key, 0)
            part_width = (value / total) * width
            
            r, g, b = colors[part]
            cr.set_source_rgb(r, g, b)
            cr.rectangle(current_x, 0, part_width, height)
            cr.fill()
            
            current_x += part_width

    def update(self):
        self.queue_draw()

class MemoryView(Gtk.Box):
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.set_border_width(10)
        
        static_info = memory_info.get_static_memory_info()
        self.total_mem_str = static_info.get("total_gb", "")
        self.commit_total = static_info.get("commit_total_gb", 0)

        # Title
        title_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        mem_label = Gtk.Label(label="Memory")
        mem_label.get_style_context().add_class("title-1")
        total_mem_label = Gtk.Label(label=self.total_mem_str)
        total_mem_label.set_halign(Gtk.Align.END)
        title_box.pack_start(mem_label, False, False, 0)
        title_box.pack_start(total_mem_label, True, True, 0)
        self.pack_start(title_box, False, False, 0)

        # Graph
        self.graph = MemoryHistoryGraph()
        self.pack_start(self.graph, True, True, 0)

        # Composition
        comp_label = Gtk.Label(label="Memory composition")
        comp_label.set_halign(Gtk.Align.START)
        self.pack_start(comp_label, False, False, 5)
        self.composition_bar = MemoryCompositionBar()
        self.pack_start(self.composition_bar, False, False, 0)
        
        # Details Grid
        self.details_grid = Gtk.Grid(column_spacing=40, row_spacing=5, margin_top=15)
        self.pack_start(self.details_grid, False, False, 0)

        self.detail_labels = {}
        dynamic_info = memory_info.get_dynamic_memory_info()
        
        # In use | Available
        self.add_detail("In use", dynamic_info["In use"], 0, 0)
        self.add_detail("Available", dynamic_info["Available"], 2, 0)

        # Committed | Cached
        commit_str = f"{dynamic_info['Committed']}/{self.commit_total:.1f} GB"
        self.add_detail("Committed", commit_str, 0, 1)
        self.add_detail("Cached", dynamic_info["Cached"], 2, 1)

        GLib.timeout_add(1000, self.update)
    
    def add_detail(self, key_text, value_text, col, row):
        key_label = Gtk.Label(label=key_text)
        key_label.set_halign(Gtk.Align.START)
        value_label = Gtk.Label(label=value_text)
        value_label.set_halign(Gtk.Align.START)
        value_label.get_style_context().add_class("dim-label")
        self.details_grid.attach(key_label, col, row, 1, 1)
        self.details_grid.attach(value_label, col + 1, row, 1, 1)
        self.detail_labels[key_text] = value_label

    def update(self):
        memory_info.update_dynamic_memory_info()
        self.graph.update()
        self.composition_bar.update()
        
        dynamic_info = memory_info.get_dynamic_memory_info()
        for key, label in self.detail_labels.items():
            if key == "Committed":
                label.set_text(f"{dynamic_info[key]}/{self.commit_total:.1f} GB")
            else:
                label.set_text(dynamic_info[key])
        return True

class ResourcesTab(Gtk.Box):
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.set_border_width(10)

        # Button switcher
        switcher_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        switcher_box.set_halign(Gtk.Align.CENTER)
        self.pack_start(switcher_box, False, False, 0)

        self.buttons = []
        cpu_button = Gtk.ToggleButton(label="CPU")
        mem_button = Gtk.ToggleButton(label="Memory")
        
        cpu_button.connect("toggled", self.on_button_toggled, "cpu")
        mem_button.connect("toggled", self.on_button_toggled, "memory")

        switcher_box.pack_start(cpu_button, False, False, 0)
        switcher_box.pack_start(mem_button, False, False, 0)
        self.buttons.extend([cpu_button, mem_button])

        # Stack for views
        self.stack = Gtk.Stack()
        self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
        self.stack.set_transition_duration(300)
        self.pack_start(self.stack, True, True, 0)

        cpu_view = CPUView()
        memory_view = MemoryView()
        
        self.stack.add_titled(cpu_view, "cpu", "CPU")
        self.stack.add_titled(memory_view, "memory", "Memory")

        # Set default
        cpu_button.set_active(True)

    def on_button_toggled(self, button, name):
        if button.get_active():
            self.stack.set_visible_child_name(name)
            for btn in self.buttons:
                if btn != button:
                    btn.set_active(False)
