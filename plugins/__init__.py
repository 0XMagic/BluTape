#plugin manager file
from importlib.machinery import SourceFileLoader
import info
import os

to_import = [
		(x, info.path + "plugins/" + x) for x in os.listdir(info.path + "plugins") if
		x.endswith(".py") and x != "__init__.py"
]

modules = list()


def init():
	global modules
	modules = [SourceFileLoader(name, file).load_module() for name, file in to_import]
	for m in modules:
		if "init" in dir(m):
			m.init()
