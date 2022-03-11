from objects import *
import pickle
import os
import secrets
import zipfile

hide_appdata_nag = False

def create_project():
	result = Container("root")
	save_dir_validate()
	return result


def appdata(*args):
	append = "/".join(args)
	path = os.getenv("APPDATA")
	if path is None:
		global hide_appdata_nag
		if not hide_appdata_nag:
			print("this device does not have an appdata folder (maybe linux?)")
			print("using local directory as backup")
			hide_appdata_nag = True
		return "data/" + append
	return path.replace("\\", "/") + "/Blutape/" + append

#create/confirm save directories and add them to .gitignore to prevent accidentally pushing save files
def save_dir_validate():
	folders = [
			"data/saves",
			"data/templates"
	]

	for f in folders:
		app_f = appdata(f)
		if not os.path.isdir(app_f):
			os.makedirs(app_f, exist_ok = True)

	#since malware can be injected into pickle files,
	#generate a token on first launch
	#insert it into the save file so that loading will fail unless key is known on system

	#not gonna sugar coat it, this is by all definitions DRM
	#however, it won't really be an issue because it only applies to save files
	#exporting the project will convert it into something sharable
	#importing .pop files as a project will be implemented soon(tm)

	path = appdata(".secret")
	if not os.path.isfile(path):
		gen = secrets.SystemRandom()
		rng = list(range(33, 127)) + list(range(161, 255))
		token = "".join([chr(x) for x in gen.choices(rng, k=255)])
		with open(path,"w") as io:
			io.write(token)


def get_secret():
	with open(appdata(".secret"), "r") as io:
		result = io.read()
	return result

def get_secret_b():
	with open(appdata(".secret"), "rb") as io:
		result = io.read()
	return result



def save(o: Container, wr, get_root = True):
	if wr is None:
		return False
	o.get_root().pwd = get_secret()
	s = pickle.dumps(o.get_root() if get_root else o)
	gen = secrets.SystemRandom()
	r = gen.randint(0,len(s)-1)
	s = s[:r] + get_secret_b() + s[r-1:]
	wr.write(s)
	wr.close()
	return True


def load(wr):
	if wr is None:
		return 1
	sb = get_secret_b()
	content = wr.read()
	wr.close()
	if sb not in content:
		return 2
	index = -1
	for n in range(len(content)):
		if sb[0] != content[n]:
			continue
		for i in range(len(sb)):
			if content[n + i] != sb[i]:
				break
			if i == len(sb) - 1:
				index = n
	if index == -1:
		return 2
	content = bytes([c for n, c in enumerate(content.replace(sb, b"")) if n != index])
	return pickle.loads(content)


def add_item(c: Container, s: str, *v, force_at = -1):
	if s not in data or not can_contain(c, s):
		raise Exception("invalid add")
	if "var" in data[s]["types"]:
		q = "quotes" in data[s]["types"]
		if not v:
			v = ["null"]
		result = c.add_item(None, s, v[0], value_quotes = q, force_at = force_at)
		result.add_flags(s)
	else:
		result = c.add_container(s, force_at = force_at)
		result.add_flags(s)
	return result


def apply_type_changes(o: Container):
	for n in range(len(o.content)):
		s = o.content[n].key()

		if "var" in data[s]["types"]:
			if isinstance(o.content[n], Container):
				a_name = o.content[n].name
				a_name_mode = o.content[n].name_mode
				a = add_item(o, s, force_at = n)
				a.name = a_name
				a.name_mode = a_name_mode
		elif isinstance(o.content[n], Pair):
			a_name = o.content[n].name
			a_name_mode = o.content[n].name_mode
			a = add_item(o, s, force_at = n)
			a.name = a_name
			a.name_mode = a_name_mode


def swap(o: Container, a, b):
	print(a, b)
	if b < 0 or a < 0 or a >= len(o.content) or b >= len(o.content):
		print("failed to swap due to bounds")
		return False

	k1 = o.content[a].key()
	v1 = o.content[a].value()

	k2 = o.content[b].key()
	v2 = o.content[b].value()

	tmp = o.content[a]
	o.content[a] = o.content[b]
	o.content[b] = tmp

	o.content[a].key(k2)
	o.content[a].value(v2)

	o.content[b].key(k1)
	o.content[b].value(v1)
	apply_type_changes(o)
	return True


def list_to_indented_string(to_indent: list):
	result = list()
	i = 0
	for x in to_indent:
		i -= x == "}"
		result.append("\t" * i + x)
		i += x == "{"
	return "\n".join(result)


def export_to_file(o: Container, wr):
	watermark = "\n".join([
			"//" + x for x in [
					"Made with Blutape mission generator",
					"https://github.com/0XMagic/BluTape"
			]]) + "\n"

	if wr is None:
		return
	txt = list_to_indented_string(o.export())
	wr.write(watermark + txt)


def can_contain(o: Container, s: str):
	if o.key() in data[s]["valid_in"]:
		return True
	return False


def get_available(o: Container):
	result = list()
	for s, d in data.items():
		if can_contain(o, s):
			result.append(s)
	return result


def list_available(o):
	r = get_available(o)
	print("\n".join([f"[{x}] {y}" for x, y in enumerate(r)]))
