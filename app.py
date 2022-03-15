import tkinter as tk
import os
import info, objects, macro
from color import *
from tkinter.filedialog import asksaveasfile, askopenfile
from tkinter import simpledialog
from tkinter import ttk

has_seen_warn = False
app = tk.Tk()
style = ttk.Style()
active_object = None
active_path = ""
active_export_path = ""

style.theme_create(
		'combostyle',
		parent = 'alt',
		settings = {
				'TCombobox':
					{
							'configure':
								{
										'selectbackground': COLOR_BACKGROUND_ALT,
										'fieldbackground':  COLOR_BACKGROUND_ALT,
										'background':       COLOR_TEXT_GENERIC,
										'foreground':       COLOR_TEXT_STR
								}
					}
		}
)

style.theme_use("combostyle")

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

def save_global():
	if not isinstance(active_object, objects.Container):
		print("Tried to save but the active object is invalid")
		print("If the project is not empty, this is a bug, please let me know if so!")
		return

	if not active_path or not os.path.isfile(active_path):
		print("no valid active path, running Save As instead")
		save_as_global()
		return

	print(f"attempting to Save\nactive path: {active_path}")
	io = open(active_path, "wb")
	if macro.save(active_object, io):
		print("save complete")
	else:
		print("save failed")



#to replace the save function for the button
#uses a global that matches the most recent object
def save_as_global():
	if not isinstance(active_object, objects.Container):
		print("Tried to save but the active object is invalid")
		print("If the project is not empty, this is a bug, please let me know if so!")
		return
	global active_path
	initial_dir = macro.appdata("data/saves")
	initial_file = 'blutape_save.blu'

	if active_path:
		aps = active_path.split("/")
		initial_dir = "/".join(aps[:-1])
		initial_file = aps[-1]
	print(f"attempting to Save As\nactive path: {initial_dir}/{initial_file}")

	io = asksaveasfile(
			parent = app,
			initialdir = initial_dir,
			initialfile = initial_file,
			defaultextension = ".blu",
			filetypes = [("BluTape Save", "*.blu")],
			mode = "wb",
	)
	p = None
	if io is not None:
		p = io.name

	if macro.save(active_object, io):
		print("save complete")

		active_path = p
	else:
		print("save aborted")


def open_global():
	global active_path
	initial_dir = macro.appdata("data/saves")
	initial_file = 'blutape_save.blu'

	if active_path:
		aps = active_path.split("/")
		initial_dir = "/".join(aps[:-1])
		initial_file = aps[-1]

	print(f"attempting to Open Save\nactive path: {initial_dir}/{initial_file}")

	io = askopenfile(
			parent = app,
			initialdir = initial_dir,
			initialfile = initial_file,
			defaultextension = ".blu",
			filetypes = [("BluTape Save", "*.blu")],
			mode = "rb"
	)

	p = None
	if io is not None:
		p = io.name

	o = macro.load(io)

	if not isinstance(o, objects.Container):
		if o == 1 or io is None:
			print("load aborted")
		elif o == 2:
			print("invalid load")
			simpledialog.messagebox.showerror(
					"Unable to load file: creator mismatch",
					"For security reasons, sharing saves are disallowed.\n"
					"This is due to security exploit in the file loader.\n"
					"You can still share exports."
			)
		return

	version = getattr(o, "schema", -1)

	if version != info.schema_ver:
		simpledialog.messagebox.showerror(
				"Unable to load file: ",
				"File version mismatch\n"
				f"Blutape:\t{info.schema_ver}\n"
				f"File:\t{version}"
		)
		return

	add_main_text_frames(o)
	update_top_path(o)
	main_back.configure(command = lambda: None)
	print(f"updated active path to {p}")
	active_path = p


def export_global(entire_project = True):
	if not isinstance(active_object, objects.Container):
		return

	global active_export_path

	initial_file = "mvm_mapName_missionName.pop"
	initial_dir = macro.appdata("data/exports")

	if active_export_path:
		axp_split = active_export_path.split("/")
		to_initial_dir = "/".join(axp_split[:-1])
		if os.path.isdir(to_initial_dir):
			initial_dir = to_initial_dir
		initial_file = axp_split[-1]

	print(f"attempting to Export\nactive path: {initial_dir}/{initial_file}")

	io = asksaveasfile(
			initialdir = initial_dir,
			initialfile = initial_file,
			defaultextension = ".pop",
			filetypes = [("MVM Population files", "*.pop")]
	)

	#for possible partial export support in the future
	if entire_project:
		o = active_object.get_root()
	else:
		o = active_object

	if macro.export_to_file(o, io):
		p = io.name
		print(f"exporting complete\nfile: {p}")
		active_export_path = p

	if io is not None:
		io.close()
	pass


app.wm_title(f"{app_info['title']} v{app_info['version']}")
app.geometry("x".join([str(dim) for dim in app_info["window_size"]]))
app.geometry("".join([f"+{dim}" if dim >= 0 else str(dim) for dim in app_info["window_pos"]]))
app.configure(bg = COLOR_BACKGROUND)
print(f"{app_info['title']} AppCore loaded")
main_frame = tk.Frame(app, bg = COLOR_BACKGROUND)
path_frame = tk.Frame(app, bg = COLOR_BACKGROUND)
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
		command = open_global,
		font = ("", 12)
)

top_bar_file.add_command(
		label = "Save",
		command = save_global,
		font = ("", 12)
)

top_bar_file.add_command(
		label = "Save As",
		command = save_as_global,
		font = ("", 12)
)

top_bar_file.add_command(
		label = "Export",
		command = export_global,
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

path_str = tk.StringVar()
path_str.set("root")
l_path = tk.Label(
		textvariable = path_str,
		bg = COLOR_BACKGROUND,
		fg = COLOR_TEXT_HIGHLIGHT,
		font = ('Courier New bold', 20)
)

main_text_frames = {
		"button": dict(),
		"text":   dict()
}
main_text_contents = {
		"a": dict(),
		"b": dict()
}
main_add = tk.Button(main_frame, text = "Add element", width = 32)

main_back = tk.Button(
		main_frame,
		width = 23,
		text = "back"
)

main_back.grid(row = 0, column = 0)



def update_top_path(v):
	path_str.set(v.get_path())


def export(o: objects.Container):
	def result():
		io = asksaveasfile(
				initialfile = 'mvm_mapName_missionName.pop',
				defaultextension = ".pop",
				filetypes = [("MVM Population files", "*.pop")]
		)
		print("exporting file")
		macro.export_to_file(o, io)
		if io is not None:
			io.close()

	return result


def move_up(o: objects.Container, n):
	def result():
		macro.swap(o, n, n - 1)
		add_main_text_frames(o)

	return result


def move_down(o: objects.Container, n):
	def result():
		macro.swap(o, n, n + 1)
		add_main_text_frames(o)

	return result


def add_menu(o: objects.Container):
	avail = macro.get_available(o)
	avail.sort()
	if avail:
		c = macro.add_item(o, avail[0])

		c.is_temp = True
		add_main_text_frames(o)
		main_text_popup(c)


def mtp_wrapper(o: objects.Container):
	v = o

	def result():
		main_text_popup(v)

	return result


def main_text_popup(o: objects.Container):
	print("selected ", o.key())

	def w_on_close():
		if o.is_temp:
			del_wrapper(o.parent, o.get_self_index())()
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
				add_main_text_frames(o.parent)
				w_on_close()

	top = tk.Toplevel(app, bg = COLOR_BACKGROUND)
	top.protocol("WM_DELETE_WINDOW", w_on_close)
	top.geometry("350x300")

	top.title("Set element type")
	lb = tk.Listbox(top, width = 43, bg = COLOR_BACKGROUND_ALT, fg = COLOR_TEXT_GENERIC)
	sv = tk.StringVar()

	sv.set(f"Current selection:\n{o.key()}")
	tx = tk.Text(top, width = 32, height = 1, bg = COLOR_BACKGROUND_ALT, fg = COLOR_TEXT_STR, pady = 3)
	ct = tk.Label(top, textvariable = sv, fg = COLOR_TEXT_GENERIC, bg = COLOR_BACKGROUND)

	fr = tk.Frame(top, bg = COLOR_BACKGROUND)

	nb_var = tk.IntVar()
	nb_var.set(o.name_mode)

	def nb_func(obj):
		def result():
			if nb_var.get():
				obj.configure(fg = COLOR_TEXT_STR, text = '')
				nt.grid(row = 0, column = 1, sticky = "n")
			else:
				obj.configure(fg = COLOR_TEXT_GENERIC, text = 'Custom label')
				nt.grid_forget()

		return result

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

	cb = tk.Button(top, text = "Confirm", command = btn_confirm)
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
	dx = app.winfo_x() + 135
	dy = app.winfo_y() + 64
	top.geometry(f"+{dx}+{dy}")


def back_wrapper(o: objects.Container):
	def result():
		add_main_text_frames(o.parent)
		main_back.configure(command = back_wrapper(o.parent))
		update_top_path(o.parent)

	return result


def amt_wrapper(o: objects.Container):
	def result():
		add_main_text_frames(o)
		main_back.configure(command = back_wrapper(o))
		update_top_path(o)

	return result


def del_wrapper(o: objects.Container, n):
	def result():
		o.content.pop(n)
		add_main_text_frames(o)

	return result


def txt_update_wrapper(v, b):
	def result(*args):
		if isinstance(v, objects.Pair):
			s = b.get("1.0", tk.END)
			print(s)
			if s.endswith("\n"):
				s = s[:-1]
			v.value(s)

	return result


def sel_update_wrapper(v, b, tv1):
	tv = tv1

	def result(*args):
		v.value(tv.get())
		add_main_text_frames(v.parent)

	return result


def add_main_text_frames(o: objects.Container):
	global active_object
	if o != active_object:
		active_object = o
	for x in main_text_frames["button"].values():
		for y in x.grid_slaves():
			y.grid_forget()
			y.destroy()
		x.destroy()
	for x in main_text_frames["text"].values():
		for y in x.grid_slaves():
			y.grid_forget()
			y.destroy()
		x.destroy()

	main_text_frames["button"].clear()
	main_text_frames["text"].clear()
	n = 0
	for v in o.content:

		mode = "text" if isinstance(v, objects.Pair) else "button"
		f = tk.Frame(main_frame, bg = COLOR_BACKGROUND)
		main_text_frames[mode][n] = f

		tk.Button(
				f,
				width = 32,
				text = v.key() if not v.name_mode else v.name,
				command = mtp_wrapper(v)
		).grid(row = 0, column = 2, sticky = 'w')

		if mode == "text":
			s_con, s_def = macro.get_pair_selections(v)
			if s_con:
				tv = tk.StringVar()
				"""
										width = 32,
						height = 1,
						bg = COLOR_BACKGROUND_ALT,
						fg = COLOR_TEXT_STR,
				"""
				b = ttk.Combobox(
						f,
						textvariable = tv,
						values = s_con,
						width = 32,
						height = min(len(s_con), 15),
						state = "readonly",

				)

				if v.value() not in s_con:
					v.value(s_con[s_def])
					b.current(newindex = s_def)
				else:
					b.current(newindex = [n for n, x in enumerate(s_con) if x == v.value()][0])

				b['foreground'] = COLOR_TEXT_STR

				b.option_add("*TCombobox*Listbox.background", COLOR_BACKGROUND_ALT)
				b.option_add("*TCombobox*Listbox.foreground", COLOR_TEXT_STR)

				b.option_add("*TCombobox*Listbox.SelectBackground", COLOR_BACKGROUND_ALT)
				b.option_add("*TCombobox*Listbox.SelectForeground", COLOR_TEXT_STR)

				b.bind("<KeyRelease>", sel_update_wrapper(v, b, tv))
				b.bind("<<ComboboxSelected>>", sel_update_wrapper(v, b, tv))

				if not v.is_temp: b.grid(row = 0, column = 3, sticky = 'w')
			else:
				b = tk.Text(
						f,
						width = 32,
						height = 1,
						bg = COLOR_BACKGROUND_ALT,
						fg = COLOR_TEXT_STR
				)
				b.insert(1.0, v.value())

				b.bind("<KeyRelease>", txt_update_wrapper(v, b))
				if not v.is_temp: b.grid(row = 0, column = 3, sticky = 'w')
		else:
			b = tk.Button(
					f,
					width = 16,
					text = "edit",
					command = amt_wrapper(v)
			)
			if not v.is_temp: b.grid(row = 0, column = 3, sticky = 'w', padx = 69)

		if not v.is_temp:
			db = tk.Button(f, text = "remove", command = del_wrapper(o, n), width = 9)
			mu = tk.Button(f, text = "↑", command = move_up(o, n))
			md = tk.Button(f, text = "↓", command = move_down(o, n))
			mu.grid(row = 0, column = 0, sticky = 'w')
			md.grid(row = 0, column = 1, sticky = 'w')
			db.grid(row = 0, column = 4, sticky = 'w', padx = 35)
			f.grid(row = n, column = 1, sticky = 'w')
			n += 1

	main_add.configure(command = lambda: add_menu(o))
	main_add.grid_forget()
	main_add.grid(row = n, column = 1, sticky = 'w')


l_path.grid(row = 0, column = 0, sticky = 'w')
path_frame.grid(row = 0, column = 0, sticky = 'w')
main_frame.grid(row = 1, column = 0, sticky = 'w')


def launch():
	tk.mainloop()
