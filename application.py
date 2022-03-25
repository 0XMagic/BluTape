import tkinter as tk
from tkinter import ttk
from color import *
import info
import objects
import macro
import savefile


def grid(e, r, c, **kwargs):
	e.grid(row = r, column = c, **kwargs)


def update_elements(force_update = False):
	app.focus_set()

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

	def w_on_close():
		if o.is_temp:
			elements[element_index].update(None, element_index)
			o.self_destruct()
		else:
			elements[element_index].update(o, element_index)
		update_elements()
		top.grab_release()
		top.destroy()

	def lb_update(*args):
		s = tx.get("1.0", tk.END)
		if s.endswith("\n"):
			s = s[:-1]
		if lb.size():
			lb.delete(0, last = lb.size() - 1)

		can_see = macro.get_available(o.parent)
		can_see = [x for x in can_see if s.lower() in x.lower() or not s]
		can_see.sort()
		for _n, _v in enumerate(can_see):
			lb.insert(_n, _v)
		if not can_see:
			lb.insert(0, "no results")

	def lb_click(event):
		if lb.size():
			_c = lb.nearest(event.y)
			_s = lb.get(_c)
			if _s and _s != "no results":
				sv.set("Current selection:\n" + _s)

	def btn_confirm(*args):
		if sv.get():
			#I have to set it twice for some reason
			_s = sv.get().replace("Current selection:\n", "")
			if _s != "None":
				o.name_mode = nb_var.get()
				if o.name_mode:
					_l = nt.get("1.0", tk.END).replace("\n", "")
					if _l.replace(" ", ""):
						o.name = _l

				o.key(_s)
				macro.apply_type_changes(o.parent)
				o.key(_s)

				o.is_temp = False
				w_on_close()

	def nb_func(obj):
		def result():
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

	nt = tk.Text(fr, width = 16, height = 1, bg = COLOR_BACKGROUND_ALT, fg = COLOR_TEXT_STR)

	nt.insert("1.0", o.name)

	nb.configure(command = nb_func(nb))

	tx.bind("<KeyRelease>", lb_update)
	lb.bind("<Button-1>", lb_click)

	cb = tk.Button(top, text = info.text_config.get("modify confirm", "???"), command = btn_confirm)
	_i_list = macro.get_available(o.parent)
	_i_list.sort()
	for n, v in enumerate(_i_list):
		lb.insert(n, v)
	top.grid_columnconfigure(0, weight = 1)
	tx.grid(row = 0, column = 0, sticky = "n")
	lb.grid(row = 1, column = 0, sticky = "n")
	ct.grid(row = 2, column = 0, sticky = "n")

	fr.grid(row = 3, column = 0, sticky = "n")

	nb.grid(row = 0, column = 0, sticky = "n")
	nb_func(nb)()
	cb.grid(row = 4, column = 0, sticky = "n")
	top.grab_set()
	w = 350
	h = 300
	dx = round(app.winfo_x() + app.winfo_width() / 2 - w / 2)
	dy = round(app.winfo_y() + app.winfo_height() / 2 - h / 2)

	top.geometry(f"{w}x{h}")
	top.geometry(f"+{dx}+{dy}")


def func_back():
	global active_object
	active_object = active_object.parent
	update_elements()


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
	set_active_project(new_project)


def func_export():
	savefile.export_project(app, active_project)


def set_active_project(p: objects.Project):
	global active_project
	global active_object
	active_project = p
	active_object = p.container
	update_elements()


class Element:
	def __init__(self, parent: (tk.Frame, tk.Tk)):
		self.frame = tk.Frame(parent, bg = COLOR_BACKGROUND)
		self.shift_frame = tk.Frame(self.frame, bg = COLOR_BACKGROUND)
		self.text_mode = 0
		self.var_selection = tk.StringVar()
		self.var_text = tk.StringVar()

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

		self.var_text.trace_add("write", self.func_text)
		self.text_is_busy = False
		#self.text.bind("<KeyRelease>", self.func_text)

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
		self.select.bind("<<ComboboxSelected>>", self.func_selection)

		grid(self.remove_button, 0, 0, padx = 5)
		ud = 1
		grid(self.shift_up, 0, ud % 2)
		grid(self.shift_down, 0, (ud + 1) % 2)
		grid(self.shift_frame, 0, 1, padx = 5)
		grid(self.key_button, 0, 2)

	def func_edit(self):
		if self.object is not None:
			global active_object
			active_object = self.object
			update_elements()

		pass

	def func_key(self):
		if self.object is not None:
			modify_element_window(self.object, self.get_self_index())
		pass

	def func_up(self):
		self._swap(-1)

	def func_down(self):
		self._swap(1)

	def _swap(self, offset):
		if self.object is not None:
			o = self.object.parent
			a = self.object.get_self_index()
			b = a + offset
			macro.swap(o, a, b)
			update_elements()

	def func_selection(self, *args):
		if self.object is not None:
			self.object.value(self.var_selection.get())
			self.select.selection_clear()

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

	def func_text(self, *args):
		self.object.value(self.var_text.get())

	def func_delete(self):
		if self.object is not None:
			self.object.self_destruct()
			self.update(None, self.get_self_index())

		pass

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
			v = self.object.value()
			i = s_con.index(v) if v in s_con else s_def
			self.select.current(newindex = i)
			self.object.value(s_con[i])

		if mode != self.mode:
			if mode == 0:
				self.frame.grid_forget()
			elif self.mode == 0:
				grid(self.frame, n, 0, pady = 3, sticky = "nw")

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
grid(btn_back, 0, 0, sticky = "w")
grid(lbl_path, 0, 1, sticky = "w")
grid(btn_add_element, 0, 0, sticky = "nw", pady = 5)

grid(frame_project, 0, 0, sticky = "w")
grid(frame_header, 0, 0, sticky = "w")
grid(frame_elements, 1, 0, sticky = "nw")
grid(frame_element_items, 1, 0, sticky = "nw")


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
	pass
