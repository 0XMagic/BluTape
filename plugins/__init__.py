#plugin manager file
from importlib.machinery import SourceFileLoader
import info
import os

to_import = [
		(x, info.path + "plugins/" + x) for x in os.listdir(info.path + "plugins") if
		x.endswith(".py") and x != "__init__.py"
]

modules = [SourceFileLoader(name, file).load_module() for name, file in to_import]
modules.sort(key = lambda m: getattr(m, "priority", 0), reverse = True)

def init():
	for m in modules:
		if "init" in dir(m):
			m.init()

def get(s: str):
	result = [m for m in modules if m.__name__ == s]
	if result:
		return result[0]
	else:
		return None
