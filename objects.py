import json
with open("rules.json") as fl:
	data = json.load(fl)

global_root = None


class Pair:
	def __init__(self, *args, parent = None):
		self.__key = None
		self.__value = None
		self.__key_quote = False
		self.__value_quote = False
		self.flags = list()
		self.parent = parent

		if len(args) == 2:
			self.key(args[0])
			self.value(args[1])

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
		rk = self.key()
		rv = self.value()
		if self.__key_quote:
			rk = f"\"{rk}\""
		if self.__value_quote:
			rv = f"\"{rv}\""
		return [f"{rk}\t{rv}"]


class Container:
	def __init__(self, *args, is_root = True, parent=None):
		self.__value = ""
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

	def get_root(self):
		if self.parent != self:
			return self.parent.get_root()
		return self

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
		if not self.__is_root:
			result = [self.__key, "{"] + result + ["}"]
		return result
