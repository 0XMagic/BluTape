import macro
import application
import savefile

if __name__ == "__main__":
	macro.save_dir_validate()
	savefile.reload_templates()
	project = savefile.autoload()  #generates a blank project if autoload.blu is not found
	application.set_active_project(project)
	application.launch()
