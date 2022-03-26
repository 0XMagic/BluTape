import json
import info
#if a key or value contains any of these chars, put quotes around it when exporting
force_quotes = " \t"


def check_quotes(v):
	s = str(v)
	if any([b in s for b in force_quotes]):
		if not s.startswith("\""):
			s = f"\"{s}"
		if not s.endswith("\""):
			s = f"{s}\""
	return s


with open("datafiles/json/keywords.json") as fl:
	data = json.load(fl)

with open("datafiles/json/selection.json") as fl:
	selections = json.load(fl)

with open("datafiles/icons.txt") as fl:
	icons = [x for x in fl.read().split("\n") if x and not x.startswith("//")]

data["None"] = {"valid_in": [x for x in data.keys()] + ["None"], "types": []}
data["%template%"] = {"valid_in": ["Templates"], "types": []}
data["EventChangeAttributes"]["valid_in"].append("TFBot")
selections["ClassIcon"]["content"] = icons

global_root = None


class Pair:
	def __init__(self, *args, parent = None):
		self.is_temp = False
		self.name = ""
		self.name_mode = 0
		self.schema = info.schema_ver
		self.name_override = False
		self.__key = None
		self.__value = None
		self.__key_quote = False
		self.__value_quote = False
		self.flags = list()
		self.parent = parent

		if len(args) == 2:
			self.key(args[0])
			self.value(args[1])

	def self_destruct(self):
		self.parent.content.pop(self.get_self_index())
		del self

	def get_self_index(self):
		for n, x in enumerate(self.parent.content):
			if x == self:
				return n
		return -1

	def key(self, *args, quotes = False):
		if args:
			self.__key = args[0]
			self.__key_quote = quotes
		return self.__key

	def value(self, *args, quotes = False):
		if args:
			self.__value = args[0]
			self.__value_quote = quotes
		return self.__value

	def add_flags(self, *flags):
		self.flags = list(flags)

	def has_flags(self, *flags):
		return all([flag in self.flags for flag in flags])

	def export(self):
		if self.is_temp:
			return []
		rk = check_quotes(self.key())
		rv = check_quotes(self.value())
		return [f"{rk}\t{rv}"]

	def export_json(self):
		return {
				"Pair": {
						"key":       self.key(),
						"value":     self.value(),
						"name":      self.name,
						"name_mode": self.name_mode
				}
		}


class Container:
	def __init__(self, *args, is_root = True, parent = None):
		self.is_temp = False
		self.__value = ""
		self.name = ""
		self.name_mode = 0
		self.name_override = False
		self.schema = info.schema_ver
		self.parent = self
		if parent is not None:
			self.parent = parent

		self.__is_root = is_root

		if is_root:
			global global_root
			global_root = self

		self.content = list()
		self.__key = ""
		self.flags = list()
		if args:
			self.__key = args[0]

	def self_destruct(self):
		self.parent.content.pop(self.get_self_index())
		del self

	def get_root(self):
		if self.parent != self:
			return self.parent.get_root()
		return self

	def get_self_index(self):
		for n, x in enumerate(self.parent.content):
			if x == self:
				return n
		return -1

	def add_flags(self, *flags):
		self.flags += list(flags)

	def has_flags(self, *flags):
		return all([flag in self.flags for flag in flags])

	def key(self, *args):
		if args:
			self.__key = args[0]
		return self.__key

	def value(self, *args):
		if args:
			self.__value = args[0]
		return self.__value

	def get_path(self, limit = 5):
		result = self.name if self.name_mode else self.key()
		if not self.__is_root:
			if limit:
				result = self.parent.get_path(limit = limit - 1) + "/" + result
			else:
				result = ".../" + result
		return result

	def add_item(self, k, v, key_quotes = False, value_quotes = False, force_at = -1):
		to_add = Pair(parent = self)
		to_add.key(k, quotes = key_quotes)
		to_add.value(v, quotes = value_quotes)

		if force_at == -1:
			self.content.append(to_add)
		else:
			self.content[force_at] = to_add

		return to_add

	def add_container(self, *args, force_at = -1):
		to_add = Container(*args, is_root = False, parent = self)
		if force_at == -1:
			self.content.append(to_add)
		else:
			self.content[force_at] = to_add
		return to_add

	def export(self):
		result = list()
		for content in self.content:
			result += content.export()
		if not self.__is_root and not self.is_temp:
			key = self.name if self.name_override else self.__key
			result = [key, "{"] + result + ["}"]
		return result

	def export_json(self):
		return {
				"Container": {
						"key":           self.key(),
						"name":          self.name,
						"name_override": self.name_override,
						"name_mode":     self.name_mode,
						"schema":        self.schema,
						"content":       [
								c.export_json() for c in self.content if not c.is_temp
						]

				}
		}

	def import_json(self, d):
		self.key(d["key"])
		self.name = d["name"]
		self.name_mode = d["name_mode"]
		self.name_override = d.get("name_override", False)

		if self.name_mode:
			print(f"loaded {self.name} ({self.key()})")
		else:
			print(f"loaded {self.key()}")

		for x in d["content"]:
			if "Container" in x:
				c = self.add_container()
				c.import_json(x["Container"])

			if "Pair" in x:
				self.add_item(x["Pair"]["key"], x["Pair"]["value"])

		pass


class Project:
	def __init__(self):
		self.container = Container("root")
		#blank str -> directory not set, ask user for it when needed
		self.path = ""  #save path of the project, set this on file load/saveAs
		self.project_name = "new_blutape_project"
		self.pop_directory = ""  #where to export the popfile
		self.mission_name = "new_blutape_mission"
		self.map_name = "mvm_coaltown"

	def repair_strings(self):
		if not self.map_name.startswith("mvm_"):
			self.map_name = "mvm_" + self.map_name.replace(" ", "_")
		self.mission_name = self.mission_name.replace(" ", "_")

	def export_json(self):
		return {
				"map":       self.map_name,
				"mission":   self.mission_name,
				"export_to": self.pop_directory,
				"project":   self.container.export_json()
		}

	def import_json(self, d, name):
		if name is not None:
			ns = name.split("/")
			self.path = "/".join(ns[:-1])
			self.project_name = ns[-1]
		if self.project_name.endswith(".blu"):
			self.project_name = self.project_name[:-4]
		if not isinstance(d, dict):
			d = dict(d)

		self.map_name = d.get("map", "mvm_coaltown")
		self.mission_name = d.get("mission", "new_blutape_mission")
		self.pop_directory = d.get("export_to", "")
		#the first layer is already created and should be skipped to avoid issues
		self.container.get_root().import_json(d["project"]["Container"])

	def export(self):
		return self.container.export()
