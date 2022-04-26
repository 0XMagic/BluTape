import macro
import application
import savefile
import plugins

def on_start():
	macro.save_dir_validate()
	macro.config_validate()
	savefile.reload_templates()
	project = savefile.autoload()  #generates a blank project if autoload.blu is not found
	application.set_active_project(project)
	application.func_reload_binds()
	plugins.init()
	application.launch()


if __name__ == "__main__":
	on_start()
