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
		row_amt = 4
		self.window = tk.Toplevel(master, bg = COLOR_BACKGROUND)
		self.window.wm_title("Plugin Manager")
		self.window.protocol("WM_DELETE_WINDOW", self.on_close)
		self.window.grab_set()
		self.window.focus_set()
		self.window.geometry("720x480")
		self.stuff = list()
		self.changes = dict()
		self.window.grid_columnconfigure(0, weight = 1)
		lbl = tk.Label(
				self.window, text = "Plugin changes are effective on restart", fg = COLOR_TEXT_GENERIC,
				bg = COLOR_BACKGROUND)
		lbl.grid(column = 0, row = 0)
		self.plugin_frame = tk.Frame(self.window, bg = COLOR_BACKGROUND)

		for n, kv in enumerate(plugins.items()):
			k, v = kv
			b = tk.Button(
					self.plugin_frame, text = btx(k, v["is_enabled"]),
					command = self.gen_on_press(k, n), bg = btc(v["is_enabled"]),
					width = 24
			)
			b.grid(column = n % row_amt, row = n // row_amt)
			self.stuff.append(b)
		self.plugin_frame.grid(column = 0, row = 1)
		self.button_confirm = tk.Button(
				self.window, text = "Confirm", command = lambda: self.on_confirm(),
				bg = COLOR_BACKGROUND_ALT, fg = COLOR_TEXT_GENERIC
		)
		self.button_confirm.grid(column = 0, row = 2)

	def gen_on_press(self, k, btn):
		return lambda: self.on_press(k, btn)

	def on_press(self, k, btn):
		new_state = not self.changes.get(k, plugins[k]["is_enabled"])
		self.stuff[btn]["text"] = btx(k, new_state)
		self.stuff[btn]["bg"] = btc(new_state)
		self.changes[k] = new_state

	def on_confirm(self):
		apply_changes(self.changes)
		self.on_close()

	def on_close(self):
		self.window.grab_release()
		self.window.destroy()


def btx(text: str, state: bool):
	result = "(ON)  " if state else "(OFF) "
	return f"{result}{text}"

def btc(state: bool):
	return COLOR_TEXT_STR if state else COLOR_ERROR


def apply_changes(changes: dict):
	for k, v in changes.items():
		if k not in plugins or plugins[k]["is_enabled"] == v: continue
		old_path = plugins[k]["path"]
		new_path = old_path.rstrip(".disabled") if v else old_path + ".disabled"
		if os.path.isfile(old_path):
			os.rename(old_path, new_path)
		else:
			print(f"notice: {old_path} does not exist, ignoring.")
		plugins[k]["path"] = new_path
		plugins[k]["is_enabled"] = v
