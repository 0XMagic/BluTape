import json
import info

"""
Used for generating datafiles/json/keywords.json

This script does not need to be run after installing BluTape.
keywords.json is already generated.

This script only needs to be run if any of the following are changed:
	datafiles/popfiles/*.pop
	datafiles/spreadsheets/Attributes.csv
	datafiles/json/attr_blacklist.json
"""

with open(info.path / "datafiles" / "json" / "attr_blacklist.json", "r") as j:
	blacklist = dict(json.load(j))


#filter out some of the do-nothing stats
def attribute_is_allowed(s: str):
	s = s.lower()
	return not any(
			(
					s in blacklist.get("equals", list()),
					any(s.startswith(x) for x in blacklist.get("startswith", list())),
					any(x in s for x in blacklist.get("contains", list()))
			)
	)

	pass


def get_content():
	f_list = (f.name for f in (info.path / "datafiles" / "popfiles").iterdir())
	content = list()
	for f in f_list:
		to_add = list()
		with open(info.path / "datafiles" / "popfiles" / f) as fl:
			print("reading ", f)
			for p in fl.readlines():
				p = p.replace("\n", "")
				while p.startswith("\t"):
					p = p[1:]
				p = p.replace("\t", " ")
				while "  " in p:
					p = p.replace("  ", " ")
				if p.startswith("//") or not p:
					continue
				if "//" in p:
					p = p.split("//")[0]
				while p.endswith(" "):
					p = p[:-1]
				while p.startswith(" "):
					p = p[1:]
				if not p:
					continue

				to_add.append(p)
		content.append(to_add)
	return content


def consolidate(data):
	result = dict()
	for file in data:
		parent = ["root", "temp"]
		for line in file:
			if line == "}":
				parent.pop()
				continue
			elif line == "{":
				parent.append(parent[-1])
				continue
			parent.pop()
			if line.startswith("\""):
				k = line.split("\" ")[0] + "\""
			else:
				k = line.split(" ")[0]
			k = k.replace("\"", "")
			parent.append(k)
			p = parent[-2]
			if p in ["ItemAttributes", "CharacterAttributes"] and k != "ItemName":
				continue
			if p == "Templates":
				continue
			if k not in result:
				for z in result.keys():
					if z.lower() == k.lower():
						k = z
						break
				if k not in result:
					print("registering:", k)
					result[k] = {"valid_in": list(), "types": list()}
			if len(parent) > 3:
				if parent[-3] == "Templates" or p == "Templates":
					continue

			if p not in result[k]["valid_in"]:
				result[k]["valid_in"].append(p)
			if " " in line:
				v = " ".join(line.split(" ")[1:])
				if v:
					if "var" not in result[k]["types"]:
						result[k]["types"].append("var")
				if v.startswith("\"") and v.endswith("\""):
					if "quotes" not in result[k]["types"]:
						result[k]["types"].append("quotes")
				elif v:
					n_mode = 1
					try:
						if "." in v:
							n_mode = 2
							float(v)
						else:
							int(v)
					except ValueError:
						n_mode = 0
					if n_mode == 1:
						if "int" not in result[k]["types"]:
							result[k]["types"].append("int")
					elif n_mode == 2:
						if "float" not in result[k]["types"]:
							result[k]["types"].append("float")
	return result


def attribute_fix(data: dict):
	print("updating attribute database")
	with open(info.path / "datafiles" / "spreadsheets" / "Attributes.csv") as fl:
		attrs = [x for x in fl.read().split("\n") if x and not x.startswith("//") and attribute_is_allowed(x)]
	data = {k: v for k, v in data.items() if "CharacterAttributes" not in v["valid_in"]}
	for a in attrs:
		data[a] = {"valid_in": ["CharacterAttributes", "ItemAttributes"], "types": ["float", "int", "var"]}
	print("Loaded", len(attrs), "TF2 attributes")
	return data


def get_where(content: list):
	with open(info.path / "datafiles" / "maps.txt") as fl:
		maps = fl.read().split("\n")

	result = {m: list() for m in maps}
	#bit of a hack solution, should just have the entries be linked from the start
	f_list = (f.name for f in (info.path / "datafiles" / "popfiles").iterdir())
	for k, v in zip(f_list, content):
		for m in maps:
			if m in k:
				to_add = [x[6:] for x in v if x.lower().startswith("where")]
				for a in to_add:
					if a not in result[m]:
						result[m].append(a)
						print(f"registering {m}.Where.{a}")
				break
	return result


def main():
	c = get_content()
	data = attribute_fix(consolidate(c))
	where = get_where(c)

	with open(info.path / "datafiles" / "json" / "keywords.json", "w") as fl:
		json.dump(data, fl, indent = "\t")

	with open(info.path / "datafiles" / "json" / "map_spawns.json", "w") as fl:
		json.dump(where, fl, indent = "\t")


if __name__ == "__main__":
	main()
