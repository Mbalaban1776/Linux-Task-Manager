import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib, Gdk
import psutil
import os
import signal

class ProcessesTab(Gtk.Box):
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.set_margin_top(10)
        self.set_margin_bottom(10)
        self.set_margin_start(10)
        self.set_margin_end(10)

        self.scrolled_window = Gtk.ScrolledWindow()
        self.scrolled_window.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        self.pack_start(self.scrolled_window, True, True, 0)

        self.process_store = Gtk.TreeStore(str, float, str, float, str, int, bool)

        self.process_view = Gtk.TreeView(model=self.process_store)
        self.process_view.set_rules_hint(True)
        self.selection = self.process_view.get_selection()
        self.selection.set_mode(Gtk.SelectionMode.SINGLE)
        self.selection.connect("changed", self.on_process_selected)

        self.columns = []
        self.columns_info = [
            ("Name", 0),
            ("PID", 5),
            ("CPU %", 2),
            ("Memory", 4)
        ]

        for title, col_id in self.columns_info:
            renderer = Gtk.CellRendererText()
            column = Gtk.TreeViewColumn(title, renderer)

            if title == "Name":
                def name_cell_func(column, cell, model, iter, data=None):
                    cell.set_property("markup", f"<b>{model[iter][0]}</b>" if model[iter][6] else model[iter][0])
                column.set_cell_data_func(renderer, name_cell_func)
            else:
                def make_cell_data_func(col_id):
                    def cell_data_func(column, cell, model, iter, data=None):
                        if model[iter][6]:
                            cell.set_property("text", "")
                        else:
                            value = model[iter][col_id]
                            cell.set_property("text", str(value))
                    return cell_data_func

                renderer.set_alignment(1.0, 0.5)
                column.set_cell_data_func(renderer, make_cell_data_func(col_id))
                column.set_alignment(1.0)
                if title == "CPU %":
                    column.set_sort_column_id(1)
                elif title == "Memory":
                    column.set_sort_column_id(3)
                elif title == "PID":
                    column.set_sort_column_id(5)

            column.set_resizable(True)
            column.set_expand(True)
            self.process_view.append_column(column)
            self.columns.append(column)

        self.scrolled_window.add(self.process_view)

        controls_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self.pack_start(controls_box, False, False, 0)

        self.end_process_button = Gtk.Button(label="End Process")
        self.end_process_button.set_sensitive(False)
        self.end_process_button.set_name("end_process_button")
        self.end_process_button.connect("clicked", self.on_end_process_clicked)
        controls_box.pack_start(self.end_process_button, False, False, 0)

        css_provider = Gtk.CssProvider()
        css_provider.load_from_data(b"""
GtkButton#end_process_button {
    background-image: none;
    background-color: #ed333b;
    color: white;
    border-radius: 6px;
    border: 1px solid #c01c28;
}
GtkButton#end_process_button:active {
    background-color: #c01c28;
}
GtkButton#end_process_button:hover {
    background-color: #f03939;
}
GtkButton#end_process_button:disabled {
    background-color: #ed333b;
    color: white;
    opacity: 0.5;
}
""")
        screen = Gdk.Screen.get_default()
        Gtk.StyleContext.add_provider_for_screen(screen, css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

        self.initialize_cpu_tracking()
        self.update_process_list()
        self.refresh_timer = GLib.timeout_add_seconds(2, self.update_process_list)

    def initialize_cpu_tracking(self):
        for proc in psutil.process_iter(['pid']):
            try:
                proc.cpu_percent(interval=None)
            except:
                pass

    def is_app(self, proc):
        try:
            name = proc.name().lower()
            gui_keywords = ['gnome', 'code', 'firefox', 'chrome', 'nautilus', 'xorg', 'wayland']
            return any(kw in name for kw in gui_keywords)
        except:
            return False

    def update_process_list(self):
        vadj = self.scrolled_window.get_vadjustment()
        scroll_value = vadj.get_value()

        selected_pid = None
        model, iter = self.selection.get_selected()
        if iter and not model[iter][6]:
            selected_pid = model[iter][5]

        self.process_store.clear()

        app_count = 0
        bg_count = 0
        apps_iter = self.process_store.append(None, ["Apps", 0.0, "", 0.0, "", 0, True])
        background_iter = self.process_store.append(None, ["Background processes", 0.0, "", 0.0, "", 0, True])

        for proc in psutil.process_iter(['pid', 'name', 'memory_info']):
            try:
                pid = proc.pid
                name = proc.name()
                mem = proc.memory_info().rss / (1024 * 1024)
                mem_str = f"{mem:.1f} MB"
                cpu = proc.cpu_percent(interval=None)
                cpu_str = f"{cpu:.1f} %"
                row = [name, cpu, cpu_str, mem, mem_str, pid, False]
                if self.is_app(proc):
                    app_count += 1
                    self.process_store.append(apps_iter, row)
                else:
                    bg_count += 1
                    self.process_store.append(background_iter, row)
            except:
                pass

        self.process_store.set_value(apps_iter, 0, f"Apps ({app_count})")
        self.process_store.set_value(background_iter, 0, f"Background processes ({bg_count})")

        if apps_iter:
            self.process_view.expand_row(self.process_store.get_path(apps_iter), False)
        if background_iter:
            self.process_view.expand_row(self.process_store.get_path(background_iter), False)

        def restore_scroll():
            vadj.set_value(scroll_value)
            return False
        GLib.idle_add(restore_scroll)

        if selected_pid is not None:
            def restore_selection():
                def search(model, path, iter, data):
                    if model[iter][5] == data:
                        self.selection.select_iter(iter)
                        return True
                    return False
                self.process_store.foreach(search, selected_pid)
                return False
            GLib.idle_add(restore_selection)

        return True

    def on_process_selected(self, selection):
        model, treeiter = selection.get_selected()
        if treeiter is not None:
            is_header = model.get_value(treeiter, 6)
            self.end_process_button.set_sensitive(not is_header)

    def on_end_process_clicked(self, button):
        model, treeiter = self.selection.get_selected()
        if treeiter is not None:
            pid = model.get_value(treeiter, 5)
            try:
                os.kill(pid, signal.SIGTERM)
                self.update_process_list()
            except ProcessLookupError:
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
