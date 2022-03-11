from objects import *
import pickle


def create_project():
	result = Container("root")
	return result


def save(o: Container, wr):
	if wr is None:
		return

	s = pickle.dumps(o.get_root())
	wr.write(s)


def load(wr):
	if wr is None:
		return
	result = pickle.load(wr)
	return result


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
