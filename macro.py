from objects import *
import os
import templates
import shutil


def create_project():
	result = Container("root")
	save_dir_validate()
	return result


def save_dir_validate():
	folders = [
			"saves",
			"templates",
			"exports",
			"projects"
	]

	for f in folders:
		app_f = info.save_dir + f
		if not os.path.isdir(app_f):
			os.makedirs(app_f, exist_ok = True)


def contains(obj: Container, s: str):
	return s in [x.key() for x in obj.content]


def config_validate():
	c_def = info.path + "datafiles/default_config/"
	files = [x for x in os.listdir(c_def) if x != "info.txt"]
	if not os.path.isdir(info.config_dir):
		os.makedirs(info.config_dir, exist_ok = True)

	for f in files:
		if not os.path.isfile(info.config_dir + f):
			shutil.copyfile(c_def + f, info.config_dir + f)


def add_item(c: Container, s: str, *v, force_at = -1):
	if "var" in data[s]["types"]:
		q = "quotes" in data[s]["types"]
		if not v:
			v = [""]
		result = c.add_item(s, v[0], value_quotes = q, force_at = force_at)
		result.add_flags(s)
	else:
		result = c.add_container(s, force_at = force_at)
		result.add_flags(s)
	return result


def apply_type_changes(o: Container):
	for n in range(len(o.content)):
		s = o.content[n].key()
		if s not in data:
			s = "None"
			o.content[n].key(s)

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


def swap(o: Container, a, b, on_finish = None):
	if b < 0 or a < 0 or a >= len(o.content) or b >= len(o.content):
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
	if on_finish:
		on_finish()
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
		return False
	txt = list_to_indented_string(o.export())
	wr.write(watermark + txt)
	return True


def can_contain(o: Container, s: str):
	key = o.key()
	if key == "%template%":
		key = "TFBot"

	if key in data[s]["valid_in"]:

		if "CharacterAttributes" in data[s]["valid_in"]:
			lim = 2
		else:
			lim = selections.get(s, dict()).get("lim", 0)

		if lim == 1:
			return is_selection_available(o, s)
		if lim == 2:
			return len([x.key() for x in o.content if x.key() == s and not x.is_temp]) == 0
		return True
	return False


def get_available(o: Container):
	result = list()
	key = o.key()
	if key == "Templates":
		return ["%template%"]
	for s, d in data.items():
		if can_contain(o, s) and s != "None":
			result.append(s)
	return result


def list_available(o):
	r = get_available(o)
	print("\n".join([f"[{x}] {y}" for x, y in enumerate(r)]))


def get_pair_selections(o: Pair):
	key = o.key()
	r = selections.get(key, dict())
	con, d = r.get("content", list()), r.get("default", 0)
	if selections.get(key, dict()).get("use_template_files"):
		con = [x for x in list(templates.active_bases.keys()) if x != "active_project"]
	if selections.get(key, dict()).get("use_active_templates"):
		con = templates.get_all_active()
	is_list = len(con) != 0
	others = [x.value() for x in o.parent.content if x.key() == key]
	con = [x for x in con if x not in others]
	if is_list and o.value():
		con = [o.value()] + [x for x in con if x != o.value()]

	if d > len(con):
		d = 0
	return con, d


def is_selection_available(o: Container, key: str):
	r = selections.get(key, dict())
	used = [x.value() for x in o.content if x.key() == key]
	if r.get("use_template_files"):
		content = [x for x in list(templates.active_bases.keys()) if x != "active_project"]
	else:
		content = r.get("content", list())
	con = [x for x in content if x not in used]
	return len(con) != 0


def should_update_bases(obj):
	return any(selections.get(i.key(), dict()).get("use_active_templates") for i in obj.content)


def update_bases(obj):
	for x in templates.active_bases:
		templates.active_bases[x] = (x == "active_project")
	for x in obj.get_root().content:
		if selections.get(x.key(), dict()).get("use_template_files", False):
			templates.active_bases[x.value()] = True
