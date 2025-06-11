import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib, Gdk, GdkPixbuf
import psutil
import os
import signal
from ui.icon_manager import IconManager

class ProcessesTab(Gtk.Box):
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.set_margin_top(10)
        self.set_margin_bottom(10)
        self.set_margin_start(10)
        self.set_margin_end(10)

        self.icon_manager = IconManager()

        self.placeholder_text = "Search processes and users"
        self.search_entry = Gtk.SearchEntry()
        self.search_entry.set_halign(Gtk.Align.CENTER)
        self.search_entry.set_width_chars(50)
        self.search_entry.set_margin_bottom(6)
        self.search_entry.connect("search-changed", self.on_search_changed)
        self.search_entry.connect("key-press-event", self.on_search_key_press)
        self.search_entry.connect("focus-out-event", self.on_search_focus_out)
        self.pack_start(self.search_entry, False, False, 0)
        self.search_entry.set_no_show_all(True)
        self.search_entry.hide()

        self.scrolled_window = Gtk.ScrolledWindow()
        self.scrolled_window.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        self.pack_start(self.scrolled_window, True, True, 0)

        self.process_store = Gtk.TreeStore(str, float, str, float, str, int, int, bool, str, str)
        self.filter = self.process_store.filter_new()
        self.filter.set_visible_func(self.filter_func)
        self.sortable_model = Gtk.TreeModelSort(model=self.filter)

        self.process_view = Gtk.TreeView(model=self.sortable_model)
        self.process_view.set_rules_hint(True)
        self.selection = self.process_view.get_selection()
        self.selection.set_mode(Gtk.SelectionMode.SINGLE)
        self.selection.connect("changed", self.on_process_selected)

        self.columns = []
        self.columns_info = [
            ("Name", 0),
            ("PID", 5),
            ("Threads", 6),
            ("CPU %", 2),
            ("Memory", 4)
        ]

        for title, col_id in self.columns_info:
            if title == "Name":
                col = Gtk.TreeViewColumn(title)
                
                pixbuf_renderer = Gtk.CellRendererPixbuf()
                col.pack_start(pixbuf_renderer, False)
                
                text_renderer = Gtk.CellRendererText()
                col.pack_start(text_renderer, True)
                
                def name_cell_data_func(column, cell, model, iter, data):
                    is_header = model.get_value(iter, 7)
                    if is_header:
                        text_renderer.set_property("markup", model.get_value(iter, 9))
                        pixbuf_renderer.set_property("icon-name", None)
                    else:
                        text_renderer.set_property("markup", "")
                        text_renderer.set_property("text", model.get_value(iter, 0))
                        pixbuf_renderer.set_property("icon-name", model.get_value(iter, 8))

                col.set_cell_data_func(text_renderer, name_cell_data_func)
                
                self.process_view.append_column(col)
                self.columns.append(col)
            else:
                renderer = Gtk.CellRendererText()
                column = Gtk.TreeViewColumn(title, renderer)

                def make_cell_data_func(col_id):
                    def cell_data_func(column, cell, model, iter, data=None):
                        is_header = model[iter][7]
                        if is_header:
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
                elif title == "Threads":
                    column.set_sort_column_id(6)

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
GtkButton#end_process_button.suggested-action {
    background-image: none;
    background-color: #3d84e0;
    color: white;
    border-radius: 6px;
    border: 1px solid #2a75d2;
}
GtkButton#end_process_button.suggested-action:active {
    background-color: #2a75d2;
}
GtkButton#end_process_button.suggested-action:hover {
    background-color: #4a90e2;
}
GtkButton#end_process_button.suggested-action:disabled {
    background-color: #3d84e0;
    color: white;
    opacity: 0.5;
}
SearchEntry.placeholder {
    color: shade(@theme_fg_color, 0.5);
    font-style: italic;
}
""")
        screen = Gdk.Screen.get_default()
        Gtk.StyleContext.add_provider_for_screen(screen, css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

        self.on_search_focus_out(self.search_entry, None)

        self.initialize_cpu_tracking()
        self.update_process_list()
        self.refresh_timer = GLib.timeout_add_seconds(2, self.update_process_list)

    def on_search_clicked(self, button):
        is_visible = self.search_entry.get_visible()
        self.search_entry.set_visible(not is_visible)
        
        if self.search_entry.get_visible():
            self.search_entry.grab_focus()
            self.on_search_focus_out(self.search_entry, None)
            GLib.idle_add(self.search_entry.set_position, 0)
        else:
            self.search_entry.set_text("")

    def on_search_key_press(self, widget, event):
        if not event.is_modifier:
            context = widget.get_style_context()
            if context.has_class("placeholder"):
                context.remove_class("placeholder")
                widget.set_text("")
        return False

    def on_search_changed(self, search_entry):
        self.filter.refilter()

    def on_search_focus_out(self, widget, event):
        if widget.get_text() == "":
            widget.get_style_context().add_class("placeholder")
            widget.set_text(self.placeholder_text)
        return False

    def filter_func(self, model, iter, data):
        search_text = self.search_entry.get_text().lower()
        
        context = self.search_entry.get_style_context()
        if not search_text or context.has_class("placeholder"):
            return True

        is_header = model[iter][7]
        if is_header:
            child_iter = model.iter_children(iter)
            while child_iter:
                if self.filter_func(model, child_iter, data):
                    return True
                child_iter = model.iter_next(child_iter)
            return False

        name = model[iter][0].lower()
        pid = str(model[iter][5])
        return search_text in name or search_text in pid

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
        if iter:
            filter_iter = self.sortable_model.convert_iter_to_child_iter(iter)
            source_iter = self.filter.convert_iter_to_child_iter(filter_iter)
            if source_iter and not self.process_store[source_iter][7]:
                 selected_pid = self.process_store[source_iter][5]

        self.process_store.clear()

        app_count = 0
        bg_count = 0
        apps_iter = self.process_store.append(None, ["", 0.0, "", 0.0, "", 0, 0, True, None, ""])
        background_iter = self.process_store.append(None, ["", 0.0, "", 0.0, "", 0, 0, True, None, ""])

        for proc in psutil.process_iter(['pid', 'name', 'memory_info']):
            try:
                pid = proc.pid
                name = proc.name()
                threads = proc.num_threads()
                icon_name = self.icon_manager.get_icon_for_process(name)
                mem = proc.memory_info().rss / (1024 * 1024)
                mem_str = f"{mem:.1f} MB"
                cpu = proc.cpu_percent(interval=None)
                cpu_str = f"{cpu:.1f} %"
                row = [name, cpu, cpu_str, mem, mem_str, pid, threads, False, icon_name, ""]
                if self.is_app(proc):
                    app_count += 1
                    self.process_store.append(apps_iter, row)
                else:
                    bg_count += 1
                    self.process_store.append(background_iter, row)
            except:
                pass

        if app_count > 0:
            self.process_store.set_value(apps_iter, 9, f"<b>Apps ({app_count})</b>")
        else:
            self.process_store.remove(apps_iter)
        
        if bg_count > 0:
            self.process_store.set_value(background_iter, 9, f"<b>Background processes ({bg_count})</b>")
        else:
            self.process_store.remove(background_iter)

        if app_count > 0:
            self.process_view.expand_row(self.process_store.get_path(apps_iter), False)
        if bg_count > 0:
            self.process_view.expand_row(self.process_store.get_path(background_iter), False)

        def restore_scroll():
            vadj.set_value(scroll_value)
            return False
        GLib.idle_add(restore_scroll)

        if selected_pid is not None:
            def restore_selection():
                def search(model, path, iter, data):
                    if model[iter][5] == data:
                        filter_path = self.filter.convert_child_path_to_path(path)
                        if filter_path:
                            sort_path = self.sortable_model.convert_child_path_to_path(filter_path)
                            if sort_path:
                                self.selection.select_path(sort_path)
                        return True
                    return False
                self.process_store.foreach(search, selected_pid)
                return False
            GLib.idle_add(restore_selection)

        return True

    def on_process_selected(self, selection):
        model, treeiter = selection.get_selected()
        style_context = self.end_process_button.get_style_context()

        if treeiter is not None:
            filter_iter = self.sortable_model.convert_iter_to_child_iter(treeiter)
            source_iter = self.filter.convert_iter_to_child_iter(filter_iter)
            if source_iter is not None:
                is_header = self.process_store[source_iter][7]
                if not is_header:
                    self.end_process_button.set_sensitive(True)
                    style_context.add_class("suggested-action")
                    return

        self.end_process_button.set_sensitive(False)
        style_context.remove_class("suggested-action")

    def on_end_process_clicked(self, button):
        model, treeiter = self.selection.get_selected()
        if treeiter is not None:
            filter_iter = self.sortable_model.convert_iter_to_child_iter(treeiter)
            source_iter = self.filter.convert_iter_to_child_iter(filter_iter)
            if source_iter is not None:
                pid = self.process_store[source_iter][5]
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
