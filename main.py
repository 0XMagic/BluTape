from macro import *
import app

if __name__ == "__main__":
	project = create_project()
	app.add_main_text_frames(project)
	app.launch()
