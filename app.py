import tkinter as tk
import info, objects, macro
from color import *
from tkinter.filedialog import asksaveasfile, askopenfile
from tkinter import simpledialog

has_seen_warn = False
app = tk.Tk()

appdata = {
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

app.wm_title(f"{appdata['title']} v{appdata['version']}")
app.geometry("x".join([str(dim) for dim in appdata["window_size"]]))
app.geometry("".join([f"+{dim}" if dim >= 0 else str(dim) for dim in appdata["window_pos"]]))
app.configure(bg = COLOR_BACKGROUND)
print(f"{appdata['title']} AppCore loaded")
main_frame = tk.Frame(app, bg = COLOR_BACKGROUND)
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


def export(o: objects.Container):
	def result():
		io = asksaveasfile(
				initialfile = 'mvm_mapName_missionName.pop',
				defaultextension = ".pop",
				filetypes = [("MVM Population files", "*.pop"), ("All Files", "*.*")]

		)
		print("exporting file")
		macro.export_to_file(o, io)
		if io is not None:
			io.close()

	return result


def save(o: objects.Container):
	def result():
		io = asksaveasfile(
				initialfile = 'blutape_save.blu',
				defaultextension = ".blu",
				filetypes = [("BluTape Save File", "*.blu"), ("All Files", "*.*")],
				mode = "wb"

		)
		print("saving file")
		macro.save(o, io)
		if io is not None:
			io.close()

	return result


def load():
	def result():
		io = askopenfile(
				initialfile = 'blutape_save.blu',
				defaultextension = ".blu",
				filetypes = [("BluTape Save File", "*.blu"), ("All Files", "*.*")],
				mode = "rb"
		)
		global has_seen_warn
		if not has_seen_warn and io is not None:
			db = simpledialog.messagebox.askyesno(
					"Save file warning",
					"Malicious save files can perform arbitrary code execution.\n"
					"ONLY OPEN SAVE FILES THAT YOU TRUST!\n"
					"Do you wish to continue loading this file?",
					icon = "warning"
			)
			if not db or db is None:
				print("rejected file load")
				io.close()
				return
			else:
				print("warning accepted")
				has_seen_warn = True

		print("loading save file")
		rs = macro.load(io)
		if io is not None:
			add_main_text_frames(rs)
			io.close()

	return result


main_export = tk.Button(
		main_frame,
		width = 23,
		text = "export"
)
main_save = tk.Button(
		main_frame,
		width = 23,
		text = "save"
)

main_load = tk.Button(
		main_frame,
		width = 23,
		text = "load"
)
main_export.grid(row = 1, column = 0)
main_save.grid(row = 2, column = 0)
main_load.grid(row = 3, column = 0)


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
	if avail:
		c = macro.add_item(o, avail[0])
		c.key(avail[0])
		print("added ", avail[0])
		add_main_text_frames(o)


def mtp_wrapper(o: objects.Container):
	v = o

	def result():
		main_text_popup(v)

	return result


def main_text_popup(o: objects.Container):
	print("selected ", o.key())

	def w_on_close():
		top.grab_release()
		top.destroy()

	def lb_update(*args):
		s = tx.get("1.0", tk.END)
		print(list(s))

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
				o.key(_s)
				macro.apply_type_changes(o.parent)
				o.key(_s)
				add_main_text_frames(o.parent)
				w_on_close()

	top = tk.Toplevel(app, bg = COLOR_BACKGROUND)
	top.protocol("WM_DELETE_WINDOW", w_on_close)
	top.geometry("350x250")

	top.title("Set element type")
	lb = tk.Listbox(top, width = 43, bg = COLOR_BACKGROUND_ALT, fg = COLOR_TEXT_GENERIC)
	sv = tk.StringVar()

	sv.set("Current selection:\nNone")
	tx = tk.Text(top, width = 32, height = 1, bg = COLOR_BACKGROUND_ALT, fg = COLOR_TEXT_STR, pady = 3)
	ct = tk.Label(top, textvariable = sv, fg = COLOR_TEXT_GENERIC, bg = COLOR_BACKGROUND)
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
	cb.grid(row = 3, column = 0, sticky = "n")
	top.grab_set()
	dx = app.winfo_x() + 64
	dy = app.winfo_y() + 64
	top.geometry(f"+{dx}+{dy}")


def back_wrapper(o: objects.Container):
	def result():
		add_main_text_frames(o.parent)
		main_back.configure(command = back_wrapper(o.parent))

	return result


def amt_wrapper(o: objects.Container):
	def result():
		add_main_text_frames(o)
		main_back.configure(command = back_wrapper(o))

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


def add_main_text_frames(o: objects.Container):
	main_export.configure(command = export(o.get_root()))
	main_save.configure(command = save(o))
	main_load.configure(command = load())
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
				text = v.key(),
				command = mtp_wrapper(v)
		).grid(row = 0, column = 2, sticky = 'w')

		if mode == "text":
			b = tk.Text(
					f,
					width = 32,
					height = 1,
					bg = COLOR_BACKGROUND_ALT,
					fg = COLOR_TEXT_STR
			)
			b.insert(1.0, v.value())
			b.grid(row = 0, column = 3, sticky = 'w')
			b.bind("<KeyRelease>", txt_update_wrapper(v, b))
		else:
			tk.Button(
					f,
					width = 16,
					text = "edit",
					command = amt_wrapper(v)
			).grid(row = 0, column = 3, sticky = 'w', padx = 69)

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


main_frame.grid(row = 0, column = 1, sticky = 'w')


def launch():
	tk.mainloop()
