import macro
import application
import savefile
if __name__ == "__main__":
	macro.save_dir_validate()
	project = savefile.autoload()
	application.set_active_project(project)
	application.launch()
