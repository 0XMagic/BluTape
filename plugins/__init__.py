#plugin manager file
from importlib.machinery import SourceFileLoader
import info

to_import = (
		(x.name, x) for x in (info.path / "plugins").iterdir() if
		x.suffix == ".py" and x.stem != "__init__"
)

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
