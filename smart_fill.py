import objects
items = list()


def cond_wrapper(st):
	def result(k):
		return k == st

	return result


def add_item(condition, function):
	if isinstance(condition, str):
		condition = cond_wrapper(condition)
	items.append((condition, function))


def run(obj: objects.Container):
	k = obj.key()
	for c, f in items:
		if c(k):
			f(obj)
			break
