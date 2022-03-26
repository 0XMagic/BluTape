content = dict()
active_bases = dict()

class Template:
	def __init__(self):
		self.name = ""
		self.popfile = ""
		self.content = list()

	def __str__(self):
		result = list()
		i = 0
		for x in [self.name] + self.content:
			i -= x == "}"
			result.append("\t" * i + x)
			i += x == "{"
		return "\n".join(result)


def reset():
	content.clear()


def load(path: str):
	in_template = False
	active_item = None
	lv = 0
	with open(path, "r") as fl:
		c = fl.read()
	for x in c.split("\n"):
		while x.startswith("\t"):
			x = x[1:]
		while x.endswith("\t") or x.endswith(" "):
			x = x[:-1]

		x = x.split("//")[0]

		if x.endswith("Templates"):
			in_template = True
			continue
		if not in_template or not x:
			continue
		if x.endswith("{"):
			lv += 1
		if x.endswith("}"):
			lv -= 1
		if lv < 0:
			break
		if lv == 1 and len(x) > 1:
			active_item = Template()
			active_item.name = x
			active_item.popfile = path.split("/")[-1]
			print(f"Loading {active_item.popfile}/{x}")
			if active_item.popfile not in active_bases:
				active_bases[active_item.popfile] = False
			content[x] = active_item
			continue

		if active_item is not None and lv > 0:
			active_item.content.append(x)

