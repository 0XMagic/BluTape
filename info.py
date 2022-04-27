import os
import pathlib

title = "BluTape"
full_title = "BluTape Mission Generator"
author = "ZeroX"
repo = "https://github.com/0XMagic/BluTape"
version = "6.7"
schema_ver = 4
window_size = (1280, 720)
window_pos = (200, 200)
path = pathlib.Path(__file__).resolve().parent

base_dir = os.getenv("APPDATA")

if base_dir is None:
	base_dir = path / title
else:
	base_dir = pathlib.Path(base_dir).resolve() / title

save_dir = base_dir / "data"
config_dir = base_dir / "config"

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
