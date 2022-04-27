#blutape clipboard manager

import pathlib
import typing
import info
import objects
import json
import macro

cache: typing.List[pathlib.Path] = list()


def sort_cache_by_date():
	global cache
	cache.sort(key = lambda x: x.stat().st_ctime, reverse = True)


def update():
	cache.clear()
	get_clip_files()


def get_clip_files():
	if not cache:
		cache.extend((info.save_dir / "clipboard").iterdir())
		sort_cache_by_date()
	return cache


def save_item(o: typing.Union[objects.Container, objects.Pair]):
	to_write = f"{o.key()}#=\"\"=" + json.dumps({"content": [o.export_json()]})
	with open(info.save_dir / "clipboard" / f"{len(cache) + 1}.clp", "w") as fl:
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
