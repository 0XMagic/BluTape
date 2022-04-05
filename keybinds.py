import json
import info
import tkinter

__all_keys = list()
__binds = dict()
__binds_default = dict()
__app_binds = list()
__app = None


def reload():
	global __binds
	global __binds_default
	with open(info.config_dir + "keybinds.json", "r") as fl:
		__binds = dict(json.load(fl))
	with open(info.path + "datafiles/default_config/keybinds.json", "r") as fl:
		__binds_default = dict(json.load(fl))

	if sorted(list(__binds.keys())) != sorted(list(__binds_default.keys())):
		__bind_combo = dict()
		for k in __binds_default.keys():
			if k in __binds:
				__bind_combo[k] = __binds[k]
			else:
				__bind_combo[k] = __binds_default[k]
		with open(info.config_dir + "keybinds.json", "w") as fl:
			json.dump(__bind_combo, fl, indent = 5)

	for d in [__binds, __binds_default]:
		for keys in d.values():
			if isinstance(keys, str):
				keys = [keys]
			for k in keys:
				if k not in __all_keys:
					__all_keys.append(k)
	clear()


def set_app(app):
	global __app
	__app = app


def bind(keyword, func):
	__app_binds.append((keyword, func))

def bind_manual(obj, keyword, func):
	kw = __binds.get(keyword, __binds_default.get(keyword, "NULL KEY"))
	if isinstance(kw, str):
		kw = [kw]
	for k in kw:
		obj.bind(k, func)

def clear():
	if isinstance(__app, tkinter.Tk):
		for kw in __all_keys:
			if isinstance(kw, str):
				kw = [kw]
			for k in kw:
				__app.unbind(k)
	__app_binds.clear()


def update():
	if not isinstance(__app, tkinter.Tk):
		return
	for keyword, func in __app_binds:
		kw = __binds.get(keyword, __binds_default.get(keyword, "NULL KEY"))
		if isinstance(kw, str):
			kw = [kw]
		for k in kw:
			__app.bind(k, func)
