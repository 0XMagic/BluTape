import os
import json

"""
Used for generating datafiles/json/keywords.json

This script does not need to be run after installing BluTape.
keywords.json is already generated.

This script only needs to be run if any of the following are changed:
	datafiles/popfiles/*.pop
	datafiles/spreadsheets/Attributes.csv  (in a future update)
"""


def get_content():
	f_list = os.listdir("datafiles/popfiles/")
	content = list()
	for f in f_list:
		to_add = list()
		with open(f"datafiles/popfiles/{f}") as fl:
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
			if k not in result:
				for z in result.keys():
					if z.lower() == k.lower():
						k = z
						break

				if k not in result:
					result[k] = {
							"valid_in":  list(),
							"types": list()
					}
			#quick fix to unify character attributes and item attributes since they both use stats
			if p in ["ItemAttributes", "CharacterAttributes"] and k != "ItemName":
				p1 = ["ItemAttributes", "CharacterAttributes"]
			else:
				p1 = [p]

			for p2 in p1:
				if p2 not in result[k]["valid_in"]:
					result[k]["valid_in"].append(p2)

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


def unify_templates(data: dict):
	all_templates = [k for k, v in data.items() if "Templates" in v["valid_in"]]
	to_apply = [k for k, v in data.items() if any(i in all_templates for i in v["valid_in"])]
	for a in to_apply: data[a]["valid_in"] += [t for t in all_templates if t not in data[a]["valid_in"]]
	return data


def main():
	content = get_content()
	data = consolidate(content)
	data = unify_templates(data)
	with open("datafiles/json/keywords.json", "w") as j:
		json.dump(data, j, indent = "\t")


if __name__ == "__main__":
	main()
