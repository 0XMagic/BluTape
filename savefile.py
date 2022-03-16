import os
import objects
import tkinter as tk
import json
import info
from tkinter.filedialog import asksaveasfile, askopenfile
import macro
fullpath = os.getenv("APPDATA")
if fullpath is None: fullpath = info.path[:-1]
fullpath = fullpath.replace("\\", "/") + "/Blutape/data/"


def save_project(parent: tk.Tk, project: objects.Project, save_as = False):
	#save as if path does not exist, or if save as is specified
	if not (project.path and os.path.isfile(project.path)) or save_as:
		if not project.path:
			project.path = "New Blutape Project"
		elif project.path.endswith(".blu"):
			project.path = project.path[:-4]
		if project.path:
			project.path = fullpath + "projects/" + project.path
		project.path += ".blu"
		path_split = project.path.split("/")
		initial_dir = "/".join(path_split[:-1])
		initial_file = path_split[-1]
		io = asksaveasfile(
				parent = parent,
				initialdir = initial_dir,
				initialfile = initial_file,
				defaultextension = ".blu",
				filetypes = [("BluTape Save", "*.blu")],
				mode = "w",
		)
	else:
		io = open(project.path, "w")

	if io is None:
		print("save aborted")
		return
	json.dump(project.export_json(), io, indent=5)
	io.close()


def load_project(parent):
	io = askopenfile(
			parent = parent,
			initialdir = fullpath + "projects/",
			defaultextension = ".blu",
			filetypes = [("BluTape Save", "*.blu")],
			mode = "r"
	)
	if io is None:
		print("load aborted")
		return
	result = objects.Project()
	result.import_json(json.load(io), io.name)
	io.close()
	return result


def export_project(parent, project: objects.Project):
	if not project.pop_directory:
		project.pop_directory = "New Blutape Project"
	elif project.pop_directory.endswith(".pop"):
		project.pop_directory = project.pop_directory.path[:-4]
	if project.pop_directory:
		project.path = fullpath + "exports/" + project.pop_directory
	project.path += ".pop"
	path_split = project.path.split("/")
	initial_dir = "/".join(path_split[:-1])
	initial_file = project.map_name + "_" + project.mission_name + ".pop"

	io = asksaveasfile(
				parent = parent,
				initialdir = initial_dir,
				initialfile = initial_file,
				defaultextension = ".pop",
				filetypes = [("MvM Mission", "*.pop")],
				mode = "w",
		)
	if io is None:
		print("export aborted")
		return
	io.write(
			macro.list_to_indented_string(
					project.export()
			)
	)
	io.close()