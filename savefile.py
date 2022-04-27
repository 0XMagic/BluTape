import pathlib
import objects
import tkinter as tk
import json
import info
from tkinter.filedialog import asksaveasfilename, askopenfilename, askdirectory
import macro
import templates
import shutil


def reload_templates():
	templates.reset()

	for s in [
			info.path / "datafiles" / "templates",
			info.save_dir / "templates"
	]:
		for p in s.iterdir():
			templates.load(p)


def save_project(parent: tk.Tk, project: objects.Project, save_as = False):
	print("Attempting save...")
	backup = (project.path, project.project_name)

	save_file = None
	if project.path is not None:
		# FIXME: If the file originally had a different extension, this will save at a different path to the original.
		# This is probably not desirable as it will just silently use a different file name than the user may expect.
		save_file = project.path / (project.project_name + ".blu")

		if not save_file.parent.is_dir() or not save_file.is_file():
			save_file = None

	if save_file is None:
		project.path = info.save_dir / "projects"
		if not save_as:
			print("Save directory not found, switching type to SaveAs")

	if save_file is None or save_as:
		save_file_name = asksaveasfilename(
				parent = parent,
				initialdir = project.path,
				initialfile = project.project_name,
				defaultextension = ".blu",
				filetypes = [("BluTape Save", "*.blu")],
		)

		if not save_file_name:
			project.path, project.project_name = backup
			print("Save aborted by user")
			return

		save_file = pathlib.Path(save_file_name).resolve()

	io = open(save_file, "w")

	project.project_name = save_file.stem
	project.path = save_file.parent
	json.dump(project.export_json(), io, indent = 5)
	print("Saved project", project.project_name, "to", project.path)
	io.close()
	return


def load_project(parent):
	print("Attempting load...")

	path = askopenfilename(
			parent = parent,
			initialdir = info.save_dir / "projects",
			defaultextension = ".blu",
			filetypes = [("BluTape Save", "*.blu")],
	)

	if not path:
		print("Load aborted by user")
		return None

	path = pathlib.Path(path).resolve()

	try:
		result = objects.Project()

		with open(path, "r") as io:
			result.import_json(json.load(io), path)

		print("Loaded project", result, "from", path.parent)
		result.container.update_templates()

		return result
	except OSError:
		print(f"Error opening file at {path}, load aborted.")

	return None


def autoload():
	a_path = info.save_dir / "projects" / "autoload.blu"
	result = objects.Project()
	if not a_path.is_file():
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

	if project.pop_directory is None or not project.pop_directory.is_dir():
		project.pop_directory = info.save_dir / "exports/"
	i_file = project.map_name + "_" + project.mission_name + ".pop"

	path = asksaveasfilename(
			parent = parent,
			initialdir = project.pop_directory,
			initialfile = i_file,
			defaultextension = ".pop",
			filetypes = [("MvM Mission", "*.pop")],
	)

	if not path:
		print("Export aborted by user.")
		return

	path = pathlib.Path(path).resolve()

	with open(path, "w") as io:
		project.pop_directory = path.parent
		print("Exported mission", i_file, "to", project.pop_directory)
		io.write(watermark + macro.list_to_indented_string(project.export()))
	return


def export_silent(project: objects.Project):
	watermark = "\n".join(["//" + x for x in [f"Made with {info.full_title}", info.repo]]) + "\n"
	i_file = int(project.map_name != "template file") * (project.map_name + "_") + (project.mission_name + ".pop")

	if project.pop_directory is None:
		print("pop_directory is None, silent export failed")
		return

	to_write = project.pop_directory

	with open(to_write / i_file, "w") as io:
		print("Exported mission", i_file, "to", project.pop_directory)
		io.write(watermark + macro.list_to_indented_string(project.export()))

	if project.copy_bases_with_export:
		for c in project.container.content:
			if c.key() == "#base":
				p_in = info.save_dir / "templates" / c.value()
				p_out = to_write + c.value()
				if p_in.is_file():
					shutil.copyfile(
							p_in,
							p_out
					)

def select_folder(location):
	i_path = location if location else info.save_dir / "exports"
	result = askdirectory(
			initialdir = i_path
	)
	return result


def select_file(flt):
	path = askopenfilename(
			filetypes = [flt],
	)

	if not path:
		return None

	return pathlib.Path(path).resolve()
