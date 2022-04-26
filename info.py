import os

title = "BluTape"
full_title = "BluTape Mission Generator"
author = "ZeroX"
repo = "https://github.com/0XMagic/BluTape"
version = 6.7
schema_ver = 4
window_size = (1280, 720)
window_pos = (200, 200)
path = "/".join(__file__.split("\\")[:-1]) + "/"

save_dir = os.getenv("APPDATA")
config_dir = os.getenv("APPDATA")
if save_dir is None:
	#fallback for linux/AppleOS
	save_dir = path + "Blutape/data/"
	config_dir = path + "Blutape/config/"
else:
	save_dir = save_dir.replace("\\", "/") + "/Blutape/data/"
	config_dir = config_dir.replace("\\", "/") + "/Blutape/config/"

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
