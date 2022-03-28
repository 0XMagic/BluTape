import os
import objects
import tkinter as tk
import json
import info
from tkinter.filedialog import asksaveasfile, askopenfile
import macro
import templates

fullpath = os.getenv("APPDATA")
if fullpath is None: fullpath = info.path[:-1]
fullpath = fullpath.replace("\\", "/") + "/Blutape/data/"


def reload_templates():
	templates.reset()

	for s in [
			info.path + "datafiles/templates",
			fullpath + "templates/"
	]:
		for p in os.listdir(s):
			templates.load(s + "/" + p)






def save_project(parent: tk.Tk, project: objects.Project, save_as = False):
	print("Attempting save...")
	backup = (project.path, project.project_name)

	if not os.path.isdir(project.path):
		project.path = fullpath + "projects/"
		if not save_as:
			print("Save directory not found, switching type to SaveAs")
		save_as = True

	elif not project.path.endswith("/"):
		project.path += "/"

	save_file = project.path + project.project_name + ".blu"
	if not os.path.isfile(save_file):
		project.project_name = "new_blutape_project"
		if not save_as:
			print("Save file name not found, switching type to SaveAs")
		save_as = True

	if save_as:
		io = asksaveasfile(
				parent = parent,
				initialdir = project.path,
				initialfile = project.project_name,
				defaultextension = ".blu",
				filetypes = [("BluTape Save", "*.blu")],
				mode = "w",
		)
	else:
		io = open(save_file, "w")

	if io is None:
		project.path = backup[0]
		project.project_name = backup[1]
		print("Save aborted")
		return

	new_path = io.name.split("/")
	project.project_name = new_path[-1][:-4]
	project.path = "/".join(new_path[:-1])
	json.dump(project.export_json(), io, indent = 5)
	print("Saved project", project.project_name, "to", project.path)
	io.close()
	return


def load_project(parent):
	print("Attempting load...")
	io = askopenfile(
			parent = parent,
			initialdir = fullpath + "projects/",
			defaultextension = ".blu",
			filetypes = [("BluTape Save", "*.blu")],
			mode = "r"
	)
	if io is None:
		print("Load aborted")
		return None
	result = objects.Project()
	result.import_json(json.load(io), io.name)
	ns = io.name.split("/")
	print("Loaded project", ns[-1], "from", "/".join(ns[:-1]))
	io.close()
	return result


def autoload():
	a_path = fullpath + "projects/autoload.blu"
	result = objects.Project()
	if not os.path.isfile(a_path):
		print("You can make a default project by naming it 'autoload.blu'")
		return result
	print("Loading default project")
	with open(a_path, "r") as fl:
		result.import_json(json.load(fl), None)
	return result


def export_project(parent, project: objects.Project):
	print("Attempting export...")
	watermark = "\n".join(["//" + x for x in [f"Made with {info.full_title}", info.repo]]) + "\n"
	project.repair_strings()
	if not os.path.isdir(project.pop_directory):
		project.pop_directory = fullpath + "exports/"
	i_file = project.map_name + "_" + project.mission_name + ".pop"
	io = asksaveasfile(
			parent = parent,
			initialdir = project.pop_directory,
			initialfile = i_file,
			defaultextension = ".pop",
			filetypes = [("MvM Mission", "*.pop")],
			mode = "w",
	)

	if io is None:
		print("export aborted")
		return

	project.pop_directory = "/".join(io.name.split("/")[:-1])
	print("Exported mission", i_file, "to", project.pop_directory)
	io.write(watermark + macro.list_to_indented_string(project.export()))
	io.close()
	return
