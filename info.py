import os
import pathlib
import typing

title = "BluTape"
full_title = "BluTape Mission Generator"
author = "ZeroX"
repo = "https://github.com/0XMagic/BluTape"
version = "6.8"
schema_ver = 4
window_size = (1280, 720)
window_pos = (200, 200)
path = pathlib.Path(__file__).resolve().parent

def get_application_dirs() -> typing.Tuple[pathlib.Path, pathlib.Path]:
	try:
		import appdirs

		# If the user has the appdirs module installed then we can use that to get the correct directories
		# the / "data" and / "config" parts are sort of redundant except on Windows where both data and config path are the same.
		save_dir = pathlib.Path(appdirs.user_data_dir(title, author, None, True)).resolve() / "data"
		config_dir = pathlib.Path(appdirs.user_config_dir(title, author, None, True)).resolve() / "config"
		return save_dir, config_dir
	except ImportError:
		return get_fallback_dirs()

def get_fallback_dirs() -> typing.Tuple[pathlib.Path, pathlib.Path]:
	# otherwise we will try and get the APPDATA environment variable
	base_dir = os.getenv("APPDATA")

	# If APPDATA environment varaible is set, we can get the config path from there.
	if base_dir is not None:
		base_dir = pathlib.Path(base_dir).resolve() / title
	# If we are on an OS that doesn't provide this environment variable
	# just use the application path (the directory containing main.py) as a base.
	else:
		base_dir = path / title

	save_dir = base_dir / "data"
	config_dir = base_dir / "config"

	return save_dir, config_dir

save_dir, config_dir = get_application_dirs()

text_config = {
		"up":                "↑",
		"down":              "↓",
		"left":              "←",
		"right":             "→",
		"delete":            "⛔ ",  #needs a space to center it
		"modify window":     "Modify Element",
		"modify window new": "New Element",
		"modify confirm":    "Confirm",
		"add element":       "Add Item",
		"edit":              "edit",
		"root splitter":     "/"
}
