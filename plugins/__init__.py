#plugin manager file
from importlib.machinery import SourceFileLoader
import info

to_import = list()
for x in (info.path / "plugins").iterdir():
	if x.name == "__pycache__" or x.name.endswith(".disabled"): continue

	if x.is_dir():
		if "__init__.py" in [y.name for y in x.iterdir()]:
			to_import.append((x.name, x / "__init__.py"))
	elif x.suffix == ".py" and x.stem != "__init__":
		to_import.append((x.name, x))

modules = [SourceFileLoader(name, str(file.resolve())).load_module() for name, file in to_import]
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
