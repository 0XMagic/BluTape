#blutape clipboard manager

import os
import info
import objects
import json
import macro

cache = list()


def sort_cache_by_date():
	global cache
	nums = list(range(len(cache)))
	times = [os.stat(x).st_ctime for x in cache]
	nums.sort(key = lambda val: times[val], reverse = True)
	cache = [cache[x] for x in nums]


def update():
	cache.clear()
	get_clip_files()


def get_clip_files():
	if not cache:
		for x in os.listdir(info.save_dir + "clipboard"):
			to_c = info.save_dir + "clipboard/" + x
			cache.append(to_c)
		sort_cache_by_date()
	return cache


def save_item(o: (objects.Container, objects.Pair)):
	to_write = f"{o.key()}#=\"\"=" + json.dumps({"content": [o.export_json()]})
	with open(info.save_dir + f"clipboard/{len(cache) + 1}.clp", "w") as fl:
		fl.write(to_write)
	update()


def load_recent(o: objects.Container):
	update()
	if not cache:
		return
	with open(cache[0], "r") as fl:
		txt = fl.read()
	k = txt.split("#=\"\"=")[0]
	if k in macro.get_available(o):
		content = txt.split("#=\"\"=")[1]
		o.import_json(json.loads(content), post = True)
