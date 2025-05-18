# src/resources/resources_view.py

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib
import cairo
from resources import resource_monitor  # this should provide get_cpu_percent() and get_memory_percent()

HISTORY_LENGTH = 100

class ResourceGraph(Gtk.Box):
    def __init__(self, title, data_func):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.data_func = data_func
        self.data = [0.0] * HISTORY_LENGTH

        self.label = Gtk.Label(label=title)
        self.drawing_area = Gtk.DrawingArea()
        self.drawing_area.set_size_request(800, 150)
        self.drawing_area.connect("draw", self.on_draw)

        self.pack_start(self.label, False, False, 0)
        self.pack_start(self.drawing_area, True, True, 0)

        GLib.timeout_add(1000, self.update)

    def update(self):
        self.data.pop(0)
        self.data.append(self.data_func())
        self.drawing_area.queue_draw()
        return True

    def on_draw(self, widget, cr):
        width = widget.get_allocated_width()
        height = widget.get_allocated_height()

        cr.set_source_rgb(1, 1, 1)
        cr.paint()

        cr.set_source_rgb(0.2, 0.6, 0.9)
        cr.set_line_width(2)
        step = width / HISTORY_LENGTH

        for i in range(1, len(self.data)):
            x1 = (i - 1) * step
            y1 = height - (self.data[i - 1] / 100) * height
            x2 = i * step
            y2 = height - (self.data[i] / 100) * height
            cr.move_to(x1, y1)
            cr.line_to(x2, y2)

        cr.stroke()


class ResourcesTab(Gtk.Box):
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.set_border_width(10)

        cpu_graph = ResourceGraph("CPU Usage (%)", resource_monitor.get_cpu_percent)
        mem_graph = ResourceGraph("Memory Usage (%)", resource_monitor.get_memory_percent)

        self.pack_start(cpu_graph, True, True, 0)
        self.pack_start(mem_graph, True, True, 0)
