import pathlib
import typing
import objects
import info

def fmt_padding(s_l: list):
	for n in range(len(s_l)):
		while s_l[n].endswith(" ") or s_l[n].endswith("\t"):
			s_l[n] = s_l[n][:-1]

		while s_l[n].startswith(" ") or s_l[n].startswith("\t"):
			s_l[n] = s_l[n][1:]
	return s_l


def fmt_starting_comment(s_l: list):
	return [x for x in s_l if not x.startswith("//") and x]


def fmt_init_replace(s: str):
	while "\n\n" in s:
		s = s.replace("\n\n", "\n")
	s = s.replace("\t", " ")
	while "  " in s:
		s = s.replace("  ", " ")
	return s


def fmt_mid_comments(s_l: list):
	for n in range(len(s_l)):
		if "//" in s_l[n]:
			ns = s_l[n]
			s_l[n] = ""
			in_quote = False
			prev = ""
			for i in range(len(ns)):
				cur = ns[0]
				ns = ns[1:]
				if cur == "/" and prev == "/" and not in_quote:
					s_l[n] = s_l[n][:-1]
					break
				if cur == "\"" or cur == "\'":
					in_quote = not in_quote
				prev = cur
				s_l[n] += cur
	return s_l


def fmt(s: str):
	s = fmt_init_replace(s)
	s_l = fmt_padding(
			fmt_mid_comments(
					fmt_starting_comment(
							fmt_padding(
									s.split("\n")
							)
					)
			)
	)
	return s_l


def get_split(s: str):
	k = ""
	in_quote = False
	while s:
		cur = s[0]
		s = s[1:]
		if cur == "\"" or cur == "\'":
			in_quote = not in_quote
		if cur == " " and not in_quote:
			break
		k += cur
	return k, s


def load_string(s: str):
	tl = fmt(s)
	p = objects.Project()
	o = p.container
	for x in tl:
		if x == "{":
			continue
		elif x == "}":
			o = o.parent
			continue
		k, v = get_split(x)
		if v:
			if k.lower() == "name" and o.key() != "%template%":
				o.name = v.replace("\"", "")
				o.name_mode = True
			else:
				k = k.replace("\"", "")

			o.add_item(k, v)
		else:
			if o.key() == "Templates":
				o = o.add_container("%template%")
				o.name_override = True
				o.name_mode = True
				o.name = k
			elif o.key() == "root":
				o = o.add_container("WaveSchedule")
			else:
				o = o.add_container(k)
	return p


def load_file(fp: typing.Union[pathlib.Path, str]):
	with open(fp, "r") as fl:
		txt = fl.read()
	return load_string(txt)


def get_example():
	return load_file(info.path / "datafiles" / "popfiles" / "robot_standard.pop")


if __name__ == "__main__":
	get_example()
