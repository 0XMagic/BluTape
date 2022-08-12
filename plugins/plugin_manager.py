import info
import os
import application
import tkinter as tk
from color import *

priority = 0
plugins = {
		x.stem: {"path": str(x), "is_enabled": x.suffix == ".py"}
		for x in (info.path / "plugins").iterdir() if
		(x.suffix == ".py" or x.suffix == ".disabled") and x.stem not in ("__init__", "plugin_manager")
}
plugin_tab = tk.Menu(
		application.top_bar, tearoff = 0, background = COLOR_BACKGROUND_ALT, foreground = COLOR_TEXT_GENERIC)


def init():
	plugin_tab.add_command(label = "Manager Plugins", command = open_manager_window, font = application.top_bar_font)
	application.top_bar.add_cascade(label = "Plugins", menu = plugin_tab, font = application.top_bar_font)
	pass


def open_manager_window():
	ManagerWindowInstance(application.app)


class ManagerWindowInstance:
	def __init__(self, master: tk.Tk):
		self.window = tk.Toplevel(master, bg = COLOR_BACKGROUND)
		self.window.wm_title("Plugin Manager")
		self.window.protocol("WM_DELETE_WINDOW", self.on_close)
		self.window.grab_set()
		self.window.focus_set()
		self.window.geometry("640x480")
		self.stuff = list()
		self.window.grid_columnconfigure(0, weight = 1)
		lbl = tk.Label(
				self.window, text = "Plugin changes are effective on restart", fg = COLOR_TEXT_GENERIC,
				bg = COLOR_BACKGROUND)
		lbl.grid(column = 0, row = 0)
		for n, kv in enumerate(plugins.items()):
			k, v = kv
			f = tk.Frame(self.window, bg = COLOR_BACKGROUND)
			b = tk.Button(
					f, text = k + ": " + ("ENABLED" if v["is_enabled"] else "DISABLED"),
					command = lambda: self.on_press(k, n), bg = COLOR_TEXT_STR if v["is_enabled"] else COLOR_ERROR)
			b.grid(column = 0, row = 0)
			f.grid(column = 0, row = n + 1)
			self.stuff.append(b)

	def on_press(self, k, btn):
		set(k, not plugins[k]["is_enabled"])
		self.stuff[btn]["text"] = k + " " + ("ENABLED" if plugins[k]["is_enabled"] else "DISABLED")
		self.stuff[btn]["bg"] = COLOR_TEXT_STR if plugins[k]["is_enabled"] else COLOR_ERROR

	def on_close(self):
		self.window.grab_release()
		self.window.destroy()


def set(k: str, state: bool):
	if k not in plugins or plugins[k]["is_enabled"] == state: return
	old_path = plugins[k]["path"]
	new_path = old_path.rstrip(".disabled") if state else old_path + ".disabled"
	os.rename(old_path, new_path)
	plugins[k]["path"] = new_path
	plugins[k]["is_enabled"] = state
