import os
import json

#used for generating rules.json
#don't need to run this if you already have rules


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
			if p in ["ItemAttributes", "CharacterAttributes"]:
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


def main():
	content = get_content()
	data = consolidate(content)
	with open("datafiles/json/rules.json", "w") as j:
		json.dump(data, j, indent = "\t")


if __name__ == "__main__":
	main()
