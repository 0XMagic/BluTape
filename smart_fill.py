#tons of hard-coded logic for autocomplete feature
#it boils down to an else-if chain for conditions of the object

import objects
import macro


def run(obj: objects.Container):
	k = obj.key()

	if k == "root":
		_root(obj)
	elif k == "WaveSchedule":
		_wave_schedule(obj)
	elif k == "Wave":
		_wave(obj)
	elif k == "WaveSpawn":
		_wave_spawn(obj)
	elif k == "TFBot" or k == "%template%":
		_tf_bot(obj)
	elif k == "ItemAttributes":
		_item_attributes(obj)


def _root(obj: objects.Container):
	if not macro.contains(obj, "WaveSchedule"):
		_wave_schedule(macro.add_item(obj, "WaveSchedule"))


def _wave_schedule(obj: objects.Container):
	if not macro.contains(obj, "StartingCurrency"):
		macro.add_item(obj, "StartingCurrency", 1000)
	else:
		_wave(macro.add_item(obj, "Wave"))


def _wave(obj: objects.Container):
	c = [
			not macro.contains(obj, "StartWaveOutput"),
			not macro.contains(obj, "DoneOutput")
	]
	if any(c):
		if c[0]:
			o = macro.add_item(obj, "StartWaveOutput")
			macro.add_item(o, "Action", "Trigger")
			macro.add_item(o, "Target", "wave_start_relay")

		if c[1]:
			o = macro.add_item(obj, "DoneOutput")
			macro.add_item(o, "Action", "Trigger")
			macro.add_item(o, "Target", "wave_finished_relay")
	else:
		macro.add_item(obj, "WaveSpawn")


def _wave_spawn(obj: objects.Container):
	c = [
			not macro.contains(obj, "Where"),
			not macro.contains(obj, "TotalCount"),
			not macro.contains(obj, "TotalCurrency"),
	]
	if any(c):

		if c[0]:
			macro.add_item(obj, "Where")

		if c[1]:
			macro.add_item(obj, "TotalCount", 1)

		if c[2]:
			macro.add_item(obj, "TotalCurrency", 100)

	else:
		_tf_bot(macro.add_item(obj, "TFBot"))


def _tf_bot(obj: objects.Container):
	c = [
			not macro.contains(obj, "Health"),
			not macro.contains(obj, "Class"),
			not macro.contains(obj, "Skill")

	]
	if any(c):
		if c[0]:
			macro.add_item(obj, "Health", 125)
		if c[1]:
			macro.add_item(obj, "Class", "Scout")
		if c[2]:
			macro.add_item(obj, "Skill", "Normal")
		return
	c = [
			not macro.contains(obj, "Item"),
			not macro.contains(obj, "CharacterAttributes"),
			not macro.contains(obj, "ItemAttributes"),
	]

	if any(c):
		if c[0]:
			macro.add_item(obj, "Item", "TF_WEAPON_SCATTERGUN")
		if c[1]:
			macro.add_item(obj, "CharacterAttributes")
		if c[2]:
			_item_attributes(macro.add_item(obj, "ItemAttributes"))


def _item_attributes(obj: objects.Container):
	if not macro.contains(obj, "ItemName"):
		p_name = "TF_WEAPON_SCATTERGUN"
		for x in obj.parent.content:
			if x.key() == "Item":
				p_name = x.value()
				break
		macro.add_item(obj, "ItemName", p_name)
