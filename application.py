import tkinter as tk
from tkinter import ttk
import json
from color import *
import info
import objects
import macro
import savefile
import templates
import keybinds
import smart_fill
import webbrowser

def grid(e, r, c, **kwargs):
	e.grid(row = r, column = c, **kwargs)


def update_sel_boxes():
	for n, x in enumerate(elements):
		if n < len(active_object.content):
			s_con, s_def = macro.get_pair_selections(active_object.content[n])
			if s_con:
				x.select['values'] = s_con


def update_elements(force_update = False):
	app.focus_set()
	if macro.should_update_bases(active_object):
		macro.update_bases(active_object)
	while len(elements) < len(active_object.content):
		to_add = Element(frame_element_items)
		elements.append(to_add)
	for n, x in enumerate(elements):
		if n < len(active_object.content):
			x.update(active_object.content[n], n, force_update = force_update)
		else:
			x.update(None, n, force_update = force_update)
	lbl_path_string.set(active_object.get_path())


def modify_element_window(o: (objects.Container, objects.Pair), element_index, add_mode = False):
	if element_index == -1:
		to_set = Element(frame_element_items)
		element_index = len(elements)
		elements.append(to_set)

	def w_on_close(*args):
		global sel_y
		if o.is_temp:
			elements[element_index].update(None, element_index)
			o.self_destruct()
		else:
			elements[element_index].update(o, element_index)
		update_elements()
		top.grab_release()
		top.destroy()
		if not o.is_temp:
			sel_y = element_index
		frame_color_update()

	def lb_update(*args):
		s = tx.get("1.0", tk.END)
		if lb.size():
			lb.delete(0, last = lb.size() - 1)
		s = s.replace("\n", "")
		can_see = macro.get_available(o.parent)
		can_see = [x for x in can_see if s.lower() in x.lower() or not s]
		can_see.sort()
		for _n, _v in enumerate(can_see):
			lb.insert(_n, _v)
		if not can_see:
			lb.insert(0, "no results")

	def lb_click(*args):
		if lb.size():
			if args[0].type is tk.EventType.ButtonPress:
				sel = [lb.nearest(args[0].y)]
			else:
				sel = lb.curselection()
			if sel:
				_s = lb.get(sel[0])
			else:
				_s = "no results"
			if _s and _s != "no results":
				sv.set("Current selection:\n" + _s)

	def btn_confirm(*args):
		if sv.get():
			_s = sv.get().replace("Current selection:\n", "")
			if _s != "None":
				o.name_mode = int(nb_var.get() or o.name_override)
				if o.name_mode:
					_l = nt.get().replace("\n", "")
					if _l.replace(" ", ""):
						o.name = _l

				o.key(_s)
				macro.apply_type_changes(o.parent)
				o.key(_s)

				o.is_temp = False
				elements[element_index].set_highlight(False)
				w_on_close()

	def nb_func(obj, alt = False):
		def result():
			if alt:
				obj.grid_forget()
				nt.grid(row = 0, column = 1, sticky = "n")
			else:
				if nb_var.get():
					obj.configure(fg = COLOR_TEXT_STR, text = '')
					nt.grid(row = 0, column = 1, sticky = "n")
				else:
					obj.configure(fg = COLOR_TEXT_GENERIC, text = 'Custom label')
					nt.grid_forget()

		return result

	top = tk.Toplevel(app, bg = COLOR_BACKGROUND)
	top.protocol("WM_DELETE_WINDOW", w_on_close)

	if add_mode:
		top.title(info.text_config.get("modify window new", "???"))
	else:
		top.title(info.text_config.get("modify window", "???"))

	lb = tk.Listbox(top, width = 43, bg = COLOR_BACKGROUND_ALT, fg = COLOR_TEXT_GENERIC)
	sv = tk.StringVar()

	sv.set(f"Current selection:\n{o.key()}")
	tx = tk.Text(top, width = 32, height = 1, bg = COLOR_BACKGROUND_ALT, fg = COLOR_TEXT_STR, pady = 3)
	ct = tk.Label(top, textvariable = sv, fg = COLOR_TEXT_GENERIC, bg = COLOR_BACKGROUND)

	fr = tk.Frame(top, bg = COLOR_BACKGROUND)

	nb_var = tk.IntVar()
	nb_var.set(o.name_mode)

	nb = tk.Checkbutton(
			fr,
			variable = nb_var, onvalue = 1, offvalue = 0,
			fg = COLOR_TEXT_GENERIC, bg = COLOR_BACKGROUND
	)

	nt = tk.Entry(fr, width = 16, bg = COLOR_BACKGROUND_ALT, fg = COLOR_TEXT_STR)

	nt.insert(0, o.name)

	nb.configure(command = nb_func(nb))

	tx.bind("<KeyRelease>", lb_update)
	lb.bind("<Button-1>", lb_click)
	lb.bind("<KeyRelease>", lb_click)

	keybinds.bind_manual(lb, "confirm", btn_confirm)
	keybinds.bind_manual(tx, "confirm", btn_confirm)
	keybinds.bind_manual(top, "confirm", btn_confirm)
	keybinds.bind_manual(top, "cancel", w_on_close)
	"""
	lb.bind("<Key>", btn_confirm)
	tx.bind("<Key>", btn_confirm)
	top.bind("<Key>", btn_confirm)
	top.bind("<Key>", w_on_close)
	"""
	cb = tk.Button(top, text = info.text_config.get("modify confirm", "???"), command = btn_confirm)
	_i_list = macro.get_available(o.parent)
	_i_list.sort()
	for n, v in enumerate(_i_list):
		lb.insert(n, v)
	w = 350
	h = 300
	top.grid_columnconfigure(0, weight = 1)

	fr.grid(row = 3, column = 0, sticky = "n")
	nb.grid(row = 0, column = 0, sticky = "n")
	mode_alt = o.key() == "%template%"
	nb_func(nb, alt = mode_alt)()
	tmp_sv = tk.StringVar()
	tmp_sv.set("Template name")
	tmp_label = tk.Label(top, textvariable = tmp_sv, fg = COLOR_TEXT_GENERIC, bg = COLOR_BACKGROUND)
	if mode_alt:
		o.name_override = True
		tmp_label.grid(row = 0, column = 0, sticky = "n")
		if not nt.get():
			nt.insert(0, "New_Template")
		nt.focus_set()
		h = 75
	else:
		tx.grid(row = 0, column = 0, sticky = "n")
		lb.grid(row = 1, column = 0, sticky = "n")
		ct.grid(row = 2, column = 0, sticky = "n")
		lb.focus_set()
	cb.grid(row = 4, column = 0, sticky = "n")
	top.grab_set()

	dx = round(app.winfo_x() + app.winfo_width() / 2 - w / 2)
	dy = round(app.winfo_y() + app.winfo_height() / 2 - h / 2)

	top.geometry(f"{w}x{h}")
	top.geometry(f"+{dx}+{dy}")


def set_active_object(o: objects.Container):
	global active_object
	if active_object.key_in_path("Templates"):
		active_object.update_templates()
	active_object = o


def func_back():
	global active_object, sel_y
	i = active_object.get_self_index()
	set_active_object(active_object.parent)
	update_elements()
	sel_y = i
	for e in elements:
		e.is_in_text = False

	frame_color_update()


def func_add_element_if_focus(*args):
	do_func = not str(args[0].widget.focus_get()).endswith("entry")
	if do_func:
		func_add_element()


def func_add_element():
	avail = macro.get_available(active_object)
	avail.sort()
	to_update = -1
	for n, x in enumerate(elements):
		if x.mode == 0:
			to_update = n
			break
	if avail:
		c = macro.add_item(active_object, avail[0])
		c.is_temp = True
		modify_element_window(c, to_update, add_mode = True)


def func_save():
	savefile.save_project(app, active_project, save_as = False)


def func_save_as():
	savefile.save_project(app, active_project, save_as = True)


def func_open_project():
	new_project = savefile.load_project(app)
	if new_project is not None:
		set_active_project(new_project)

	frame_color_update()


def func_export():
	savefile.export_project(app, active_project)


def func_reload_templates(*args):
	print("Reloading templates" + "(Keyboard shortcut)" if args else "")
	templates.reload_templates()


def set_active_project(p: objects.Project):
	global active_project
	global active_object
	active_project = p
	set_active_object(p.container)
	update_elements()


def get_highlighted():
	_a = [x for x in elements if x.is_active]
	if not _a:
		return None
	return _a[0]


def arrow_up_move(*args):
	in_focus = str(args[0].widget.focus_get()).endswith("entry")
	if in_focus:
		return
	a = get_highlighted()
	if a is not None:
		a.func_up()
	frame_color_update()


def arrow_down_move(*args):
	in_focus = str(args[0].widget.focus_get()).endswith("entry")
	if in_focus:
		return
	a = get_highlighted()
	if a is not None:
		a.func_down()
	frame_color_update()


def arrow_up(*args):
	in_focus = str(args[0].widget.focus_get())
	if in_focus.endswith("entry") or in_focus.endswith("combobox"):
		return
	global sel_y
	if sel_y > 0:
		sel_y -= 1
	frame_color_update()


def arrow_down(*args):
	in_focus = str(args[0].widget.focus_get())
	if in_focus.endswith("entry") or in_focus.endswith("combobox"):
		return
	global sel_y
	sel_y += 1
	frame_color_update()


def arrow_left(*args):
	in_focus = str(args[0].widget.focus_get()).endswith("entry")
	if in_focus:
		return
	func_back()


def element_action(*args):
	a = get_highlighted()
	if a is not None:
		if a.mode == 1:
			in_focus = str(args[0].widget.focus_get()).endswith("entry")
			if in_focus:
				return
			a.func_edit()
		elif a.mode == 2:
			in_focus = str(args[0].widget.focus_get()).endswith("entry")
			if not in_focus:
				a.text.focus_set()
			else:
				if args[0].keysym != "Right":
					app.focus_set()
		elif a.mode == 3:
			in_focus = str(args[0].widget.focus_get()).endswith("combobox")
			if not in_focus:
				a.select.focus_set()
				a.select.event_generate('<Down>')
			else:
				a.func_text_lose_focus()


def del_active(*args):
	in_focus = str(args[0].widget.focus_get())
	if in_focus.endswith("entry") or in_focus.endswith("combobox"):
		return
	a = get_highlighted()
	if a is not None:
		a.func_delete()


def change_key_active(*args):
	in_focus = str(args[0].widget.focus_get())
	if in_focus.endswith("entry") or in_focus.endswith("combobox"):
		return
	a = get_highlighted()
	if a is not None:
		a.func_key()


def frame_color_update():
	if not side_pin_var.get():
		to_text = macro.list_to_indented_string(active_object.export(max_recur = 8))
		side_text['state'] = "normal"
		side_text.delete("1.0", "end")
		side_text.insert("0.0", to_text)
		side_text['state'] = "disabled"
	global sel_y
	alive = [n for n, x in enumerate(elements) if x.mode]
	if not alive:
		return
	if sel_y >= len(alive):
		sel_y = len(alive) - 1

	for n, e in enumerate(elements):
		e.set_highlight(n == alive[sel_y])


def update_sel_y_by_object_id(o: objects.Container, val):
	global sel_y
	for n, x in enumerate(elements):
		if x.object == o.content[val]:
			sel_y = n
	frame_color_update()

def func_smart_fill(*args):
	in_focus = str(args[0].widget.focus_get()).endswith("entry")
	if in_focus:
		return
	smart_fill.run(active_object)
	global sel_y
	sel_y = max(len(elements), 0)
	update_elements()
	frame_color_update()


class Element:
	def __init__(self, parent: (tk.Frame, tk.Tk)):
		self.frame = tk.Frame(parent, bg = COLOR_BACKGROUND)
		self.shift_frame = tk.Frame(self.frame, bg = COLOR_BACKGROUND)
		self.text_mode = 0
		self.var_selection = tk.StringVar()
		self.var_text = tk.StringVar()
		self.is_active = False
		self.is_in_text = False

		self.frame.bind("<Button-1>", self.on_frame_click)

		self.mode = 0
		self.object = None
		self.key_button = tk.Button(
				self.frame, width = 32,
				command = self.func_key,
				height = 1
		)
		self.edit_button = tk.Button(
				self.frame, width = 8, text = info.text_config.get("edit", "???"),
				command = self.func_edit,
				height = 1
		)
		self.text = tk.Entry(
				self.frame,
				width = 32,
				bg = COLOR_BACKGROUND_ALT,
				fg = COLOR_TEXT_STR,
				textvariable = self.var_text
		)

		self.var_text.trace_add("write", lambda *args: self.func_text())
		self.text_is_busy = False
		keybinds.bind_manual(self.text, "cancel", lambda *args: self.func_text_lose_focus())
		#self.text.bind("<Escape>", lambda *args: self.func_text_lose_focus())
		self.text.bind("<FocusIn>", lambda *args: self.f_in())
		self.text.bind("<FocusOut>", lambda *args: self.f_out())

		self.remove_button = tk.Button(
				self.frame, width = 2,
				text = info.text_config.get("delete", "???"), fg = COLOR_ERROR,
				command = self.func_delete
		)
		self.shift_up = tk.Button(
				self.shift_frame,
				text = info.text_config.get("up", "???"),
				command = self.func_up,
				width = 1,
				height = 1
		)
		self.shift_down = tk.Button(
				self.shift_frame,
				text = info.text_config.get("down", "???"),
				command = self.func_down,
				width = 1,
				height = 1
		)
		self.select = ttk.Combobox(
				self.frame,
				width = 32,
				state = "readonly",
				textvariable = self.var_selection
		)
		#to set in activate: height and values
		self.select['foreground'] = COLOR_TEXT_STR

		self.select.option_add("*TCombobox*Listbox.background", COLOR_BACKGROUND_ALT)
		self.select.option_add("*TCombobox*Listbox.foreground", COLOR_TEXT_STR)
		self.select.option_add("*TCombobox*Listbox.SelectBackground", COLOR_BACKGROUND_ALT)
		self.select.option_add("*TCombobox*Listbox.SelectForeground", COLOR_TEXT_STR)
		self.select.bind("<<ComboboxSelected>>", lambda *args: self.func_selection())
		self.select.bind("<FocusIn>", lambda *args: self.f_in())

		grid(self.remove_button, 0, 0, padx = 5)
		ud = 1
		grid(self.shift_up, 0, ud % 2)
		grid(self.shift_down, 0, (ud + 1) % 2)
		grid(self.shift_frame, 0, 1, padx = 5)
		grid(self.key_button, 0, 2)

	def on_frame_click(self, event):
		if event.x <= 750:
			global sel_y
			sel_y = self.get_self_index()
			frame_color_update()

	def f_in(self):
		global sel_y
		if self.is_in_text and self.mode == 3 and str(self.select.focus_get()).endswith("combobox"):
			self.select.event_generate("<Return>")
		self.is_in_text = True
		sel_y = self.get_self_index()
		frame_color_update()

	def f_out(self):
		self.is_in_text = False
		frame_color_update()

	def set_highlight(self, b: bool):
		b1 = self.is_in_text and self.mode != 3
		to_set = COLOR_MENU_HIGHLIGHT if b and not b1 else COLOR_BACKGROUND_ALT
		self.is_active = b
		self.frame["bg"] = to_set
		self.shift_frame["bg"] = to_set

		tb = COLOR_TEXT_NUM if self.text_mode else COLOR_TEXT_STR

		self.text["bg"] = tb if b1 and b else COLOR_BACKGROUND_ALT
		self.text["fg"] = COLOR_BACKGROUND_ALT if b1 else tb

	def func_edit(self):
		if self.object is not None:
			global active_object, sel_y
			set_active_object(self.object)
			sel_y = 0

			for e in elements:
				e.is_in_text = False

			update_elements()
			frame_color_update()

	@staticmethod
	def func_text_lose_focus():
		app.focus_force()

	def func_key(self):
		if self.object is not None:
			modify_element_window(self.object, self.get_self_index())

	def func_up(self):
		self._swap(-1)

	def func_down(self):
		self._swap(1)

	def _swap(self, offset):
		if self.object is not None:
			o = self.object.parent
			a = self.object.get_self_index()
			b = a + offset
			c = a if sel_y == self.get_self_index() else b
			macro.swap(o, a, b, on_finish = lambda: update_sel_y_by_object_id(o, c))
			update_elements()

	def func_selection(self):
		if self.object is not None:
			self.object.value(self.var_selection.get())
			self.select.selection_clear()
			self.func_text_lose_focus()

	def get_text_mode(self):
		mode = 0
		if self.object is not None:
			if "int" in objects.data.get(self.object.key(), dict()).get("types", list()):
				mode = 1
			if "float" in objects.data.get(self.object.key(), dict()).get("types", list()):
				mode = 2
			elif self.object.parent.key() in [
					"ItemAttributes",
					"CharacterAttributes"
			] and self.object.key() != "ItemName":
				mode = 2
		was_changed = mode != self.text_mode
		self.text_mode = mode
		return was_changed

	def func_text(self):
		self.object.value(self.var_text.get())

	def func_delete(self):
		if self.object is not None:
			self.object.self_destruct()
			self.update(None, self.get_self_index())
			update_sel_boxes()
			frame_color_update()

	def get_self_index(self):
		return [n for n, x in enumerate(elements) if x == self][0] if self in elements else -1

	def update(self, obj, n, force_update = False):
		self.object = obj

		s_con, s_def = list(), 0
		if isinstance(obj, objects.Container):
			mode = 1
		elif isinstance(obj, objects.Pair):
			mode = 2
		else:
			mode = 0
		if obj is not None:
			self.key_button["text"] = obj.name if obj.name_mode else obj.key()
			s_con, s_def = macro.get_pair_selections(obj)

		if mode == 2 and s_con:
			mode = 3

		if force_update:
			self.mode = 0

		if mode == 2:
			was_changed = self.get_text_mode()
			if was_changed:
				if self.text_mode:
					self.text["width"] = 8
					self.text["fg"] = COLOR_TEXT_NUM
				else:
					self.text["width"] = 32
					self.text["fg"] = COLOR_TEXT_STR
			self.var_text.set(self.object.value())

		elif mode == 3:
			self.mode = 0
			self.select['values'] = s_con
			val = self.object.value()
			i = s_con.index(val) if val in s_con else s_def
			if s_con:
				self.select.current(newindex = i)
				self.object.value(s_con[i])
			else:
				self.object.value(None)

		if mode != self.mode:
			if mode == 0:
				self.frame.grid_forget()
			elif self.mode == 0:

				grid(self.frame, n, 0, pady = 3, sticky = "ew")

			if mode == 1:
				self.text.grid_forget()
				grid(self.edit_button, 0, 3, sticky = 'w', padx = 5)
			else:
				self.edit_button.grid_forget()

			if mode == 2:
				grid(self.text, 0, 3, sticky = 'w', padx = 5)
			elif self.mode == 2:
				self.text.grid_forget()

			if mode == 3:
				grid(self.select, 0, 3, sticky = 'w', padx = 5)
			elif self.mode == 3:
				self.select.grid_forget()
			self.mode = mode


active_project = objects.Project()  #temp objects to be overwritten by project creator
active_object = active_project.container
app = tk.Tk()
style = ttk.Style()
elements = list()
app_info = {
		key: getattr(info, key, backup) for key, backup in [
				("title", "untitled application"),
				("full_title", "untitled application (long ver)"),
				("version", "(unknown version)"),
				("window_size", (1280, 720)),
				("window_pos", (128, 128)),
				("repo", None),
				("author", "no one, apparently")

		]
}
app.wm_title(f"{app_info['title']} v{app_info['version']}")
app.geometry("x".join([str(dim) for dim in app_info["window_size"]]))
app.geometry("".join([f"+{dim}" if dim >= 0 else str(dim) for dim in app_info["window_pos"]]))
app.configure(bg = COLOR_BACKGROUND)

sel_y = 0
"""
app.bind("<Shift-A>", func_add_element_if_focus)
app.bind("<Shift-E>", change_key_active)
app.bind("<Shift-X>", del_active)
app.bind("<BackSpace>", del_active)
app.bind("<Delete>", del_active)
app.bind("<Up>", arrow_up)
app.bind("<Down>", arrow_down)
app.bind("<Left>", arrow_left)
app.bind("<Right>", element_action)
app.bind("<Return>", element_action)
app.bind("<Shift-Up>", arrow_up_move)
app.bind("<Shift-Down>", arrow_down_move)
app.bind("<Control-s>", lambda a: func_save())
app.bind("<Control-Shift-S>", lambda a: func_save_as())
app.bind("<Control-e>", lambda a: func_export())
app.bind("<Control-o>", lambda a: func_open_project())
app.bind("<Control-Shift-R>", func_reload_templates)
"""


def func_reload_binds():
	keybinds.set_app(app)
	keybinds.reload()
	print("reloading keybinds")
	keybinds.bind("interact", element_action)
	keybinds.bind("back", arrow_left)

	keybinds.bind("select up", arrow_up)
	keybinds.bind("select down", arrow_down)
	keybinds.bind("move item up", arrow_up_move)
	keybinds.bind("move item down", arrow_down_move)

	keybinds.bind("add item", func_add_element_if_focus)
	keybinds.bind("change item", change_key_active)

	keybinds.bind("open", lambda a: func_open_project())
	keybinds.bind("export", lambda a: func_open_project())
	keybinds.bind("reload templates", func_reload_templates)

	keybinds.bind("save as", lambda a: func_save_as())
	keybinds.bind("save", lambda a: func_save())
	keybinds.bind("delete", del_active)
	keybinds.bind("reload keybinds", lambda a: func_reload_binds())
	keybinds.bind("smart fill", func_smart_fill)

	keybinds.update()
	global sel_y
	sel_y = 0
	for e in elements:
		e.frame.destroy()
	elements.clear()
	update_elements()


lbl_path_string = tk.StringVar()
lbl_path_string.set("root")
frame_project = tk.Frame(app, bg = COLOR_BACKGROUND)
frame_header = tk.Frame(frame_project, bg = COLOR_BACKGROUND)
frame_elements = tk.Frame(frame_project, bg = COLOR_BACKGROUND)
frame_element_items = tk.Frame(frame_elements, bg = COLOR_BACKGROUND)

top_bar = tk.Menu(
		app,
		activebackground = COLOR_TEXT_HIGHLIGHT,

		#these kwargs only work on linux
		background = COLOR_BACKGROUND_ALT,
		foreground = COLOR_TEXT_GENERIC
)

top_bar_file = tk.Menu(
		top_bar,
		tearoff = 0,
		background = COLOR_BACKGROUND_ALT,
		foreground = COLOR_TEXT_GENERIC
)

top_bar_file.add_command(
		label = "Open",
		command = func_open_project,
		font = ("", 12)
)

top_bar_file.add_command(
		label = "Save",
		command = func_save,
		font = ("", 12)
)

top_bar_file.add_command(
		label = "Save As",
		command = func_save_as,
		font = ("", 12)
)

top_bar_file.add_command(
		label = "Export",
		command = func_export,
		font = ("", 12)
)

top_bar.add_cascade(
		label = "File",
		menu = top_bar_file,
		font = ("", 12)
)

top_bar_reload = tk.Menu(
		top_bar,
		tearoff = 0,
		background = COLOR_BACKGROUND_ALT,
		foreground = COLOR_TEXT_GENERIC
)

top_bar_reload.add_command(
		label = "Templates",
		command = func_reload_templates,
		font = ("", 12)
)

top_bar_reload.add_command(
		label = "Keybinds",
		command = func_reload_binds,
		font = ("", 12)
)

top_bar.add_cascade(
		label = "Reload",
		menu = top_bar_reload,
		font = ("", 12)
)

top_bar_help = tk.Menu(
		top_bar,
		tearoff = 0,
		background = COLOR_BACKGROUND_ALT,
		foreground = COLOR_TEXT_GENERIC
)


def open_url_wrapper(_v):
	def result():
		print("opening",_v)
		webbrowser.open(_v)

	return result

with open(info.path+"datafiles/help_url.json", "r") as _fl:
	_js = dict(json.load(_fl))

	for k, v in _js.items():
		top_bar_help.add_command(
				label = k,
				command = open_url_wrapper(v),
				font = ("", 12)
		)


top_bar.add_cascade(
		label = "Guides",
		menu = top_bar_help,
		font = ("", 12)
)

app.configure(
		menu = top_bar
)

btn_back = tk.Button(
		frame_header,
		width = 2,
		height = 1,
		text = info.text_config.get("left", "???"),
		command = func_back
)

lbl_path = tk.Label(
		frame_header,
		textvariable = lbl_path_string,
		bg = COLOR_BACKGROUND,
		fg = COLOR_TEXT_HIGHLIGHT,
		font = ('Courier New bold', 20)
)

btn_add_element = tk.Button(
		frame_elements,
		width = 32,
		height = 2,
		text = info.text_config.get("add element", "???"),
		command = func_add_element
)
side_text = tk.Text(
		frame_elements,
		bg = COLOR_BACKGROUND,
		fg = COLOR_TEXT_GENERIC,
		state = "disabled"
)

side_pin_var = tk.IntVar()
side_pin = tk.Checkbutton(
		frame_elements,
		bg = COLOR_BACKGROUND,
		fg = COLOR_TEXT_HIGHLIGHT,
		text = "Pin view",
		variable = side_pin_var,
		onvalue = 1,
		offvalue = 0,
		command = frame_color_update,
)

grid(btn_back, 0, 0, sticky = "w")
grid(lbl_path, 0, 1, sticky = "w")
grid(btn_add_element, 0, 0, sticky = "nw", pady = 5)
grid(side_text, 1, 1, sticky = "nsew")
grid(side_pin, 0, 1, sticky = "e")

app.grid_columnconfigure(0, weight = 1)
frame_project.grid_columnconfigure(0, weight = 1)
frame_elements.grid_columnconfigure(0, weight = 1)
frame_element_items.grid_columnconfigure(0, weight = 1)
grid(frame_project, 0, 0, sticky = "new")
grid(frame_header, 0, 0, sticky = "nw")
grid(frame_elements, 1, 0, sticky = "new")
grid(frame_element_items, 1, 0, sticky = "new")


def style_init():
	style.theme_create(
			'combo_style',
			parent = 'alt',
			settings = {
					'TCombobox': {
							'configure': {
									'selectbackground': COLOR_BACKGROUND_ALT,
									'fieldbackground':  COLOR_BACKGROUND_ALT,
									'background':       COLOR_TEXT_GENERIC,
									'foreground':       COLOR_TEXT_STR
							}
					}
			}
	)
	style.theme_use("combo_style")


def launch():
	style_init()
	tk.mainloop()
