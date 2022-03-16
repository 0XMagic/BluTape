import objects
import macro
import application

if __name__ == "__main__":
	macro.save_dir_validate()
	blank_project = objects.Project()
	application.set_active_project(blank_project)
	application.launch()
