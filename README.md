# BLUTAPE COMPREHENSIVE GUIDE
**version 6.7**

## System requirements
* [The latest version of python](https://www.python.org/)

## Dependencies
* Blutape requires no additional dependencies


## Launching Blutape:
To launch Blutape, simply run `Blutape/main.py`\
On windows, you can run Blutape without the background terminal with `Blutape/main_no_console_windows.pyw`

## Configuration
After launching blutape for the first time, various configuration options will be placed in this directory\
`C:/Users/(user)/AppData/Roaming/Blutape/config`\
The following configuration files will be present:
* **keybinds.json**: allows for customisable keyboard shortcuts

## Default keyboard shortcuts
* **Ctrl + S**: Save
* **Ctrl + Shift + S**: Save As
* **Ctrl + E**: Export
* **Ctrl + O**: Open
* **Ctrl + P**: Project properties
* **Ctrl + I**: Import popfile
* **Ctrl + Shift + R**: Reload template files
* **Shift + A**: Add Element
* **Shift + E**: Change Element
* **Shift + X / Backspace / Delete**: Delete Element
* **Ctrl + Shift + A**: Smart fill
* **Escape / Return**: Stop editing text
* **Up/Down**: Change highlighted Element
* **Shift + Up/Down**: Shift Elements
* **Left**: Back button
* **Return / Right**: Element Action
* **Ctrl + Right**: Next page
* **Ctrl + Left**: Previous page
* **Ctrl + C**: Copy
* **Ctrl + V**: Paste


## Adding templates to the project
1. Copy the pop file with your templates into `AppData/Blutape/data/templates`.
2. Select `reload -> Templates`
3. Go to your Root node and add a #base for the added the files.\
*note: do not add templates to `Blutape\datafiles\templates`*\
*these files are not copied to the export directory*

## Having a project automatically open when launching Blutape
To make a project load on start, simply save a project as "autoload.blu"

## Implementing extra .pop features
Blutape generates it's options dynamically based on existing missions.\
These missions are located in `Blutape/datafiles/popfiles`.\
It is very possible that there are keywords that Valve never used in their missions.\
If this is true, you can update the datafiles manually by doing the following:
1. Get a mission file that uses the keyword you want to add.
2. Run `Blutape/update_datafiles.py`
3. Re-launch Blutape.

##Adding custom maps
Blutape has a preset map list that is used for generating selections for the "Where" choices.\
You can add custom maps to blutape by doing the following:
1. Open `Blutape/datafiles/maps.txt` and add the name of the map to the list.
2. Open `Blutape/datafiles/json/map_spawns.json` and add your map with a list of all of it's spawn nodes.\
*note: use an empty list to convert the related selection boxes into regular text boxes*
3. Re-launch Blutape.

##Adding custom Icons
Robot icons are in a preset list.\
You can add more by doing the following:
1. Open `Blutape/datafiles/icons.txt` and add the icon names.
2. Re-launch Blutape.

##Adding plugins
With the plugin system, python files can be added to the `Blutape/plugins` folder.\
Simply import the blutape modules you need and give it an `init()` function to start it.\
*note: blutape needs to be re-launched to activate new plugins*
