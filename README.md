# BLUTAPE COMPREHENSIVE GUIDE
**version 6.2**

## System requirements
* [The latest version of python](https://www.python.org/)

## Launching Blutape:
To launch Blutape, simply run **Blutape/main.py**

## Configuration
various configuration options are located in *info.py*.
* **title**: The title of the window.
* **full_title**: Full title of the program.
* **repo**: Url of repository (not yet implemented)
* **author**: Username of the author. Don't change this. (please)
* **version**: Display version in window title.
* **schema_ver**: Save file schema version number. (changing this may cause BluTape to be unable to load save files)
* **window_size**: Width and Height of the window.
* **window_pos**: X and Y position of the window.
* **path**: this line contains code to auto-generate it's value. ***Changing this WILL cause blutape to be unable to launch!***
* **text_config**: various text strings for button texts and sub-window titles.

## Keyboard shortcuts
#### Main Window:
* **Ctrl + S**: Save
* **Ctrl + Shift + S**: Save As
* **Ctrl + E**: Export
* **Ctrl + O**: Open
* **Ctrl + Shift + R**: Reload template files
* **Shift + A**: Add Element
* **Shift + E**: Change Element
* **Shift + X / Backspace / Delete**: Delete Element
* **Escape / Return**: Stop editing text
* **Up/Down**: Change highlighted Element
* **Shift + Up/Down**: Shift Elements
* **Left**: Back button
* **Return / Right**: Element Action

#### Modify Element Window:
* **Escape**: Cancel
* **Return**: Confirm
* **Up/Down**: Navigate listbox

## Upper menu options
### file:
* **Open**: Open a blutape save file.
* **Save** / **Save As**: Save a blutape project.
* **Export**: Compile your project into an mvm mission. For this, use your tf/scripts/population folder in your server.

### Template:
* **Reload**: Reloads template files, this is automatically run on startup and when loading save files.

## Stock menu:
* **Back arrow**: Goes up one level in the json-like tree system, if already at the root node. this will do nothing.
* **Path**: Shows where you are located in the project.
* **Add item**: Adds a new element, for more info refer to [The Element Window](#element-window). If no new elements can be added, this will do nothing.

## Element Window
* **Search bar**: Filters the items in the selection box.
* **Selection box**: The available items to add/convert to. click one to select it.
* **Custom label**: When enabled, it will display a text field to insert a custom name for the Element, this is for organisation only.
* **Confirm**: Creates an [Element](#element) with the desired options, to cancel, simply close the Element Window.

## Template Element Window
This is a modified [Element Window](#element-window) when adding an element from *Templates*. It has some unique properties.
* **Template name**: The name of the template you are creating, unlike "Custom label," this matters for the compile output.

## Element
This represents a "node" in the output popfile, it's properties can change depending on the [Element Type](#element-types).\
Listed here are buttons that are shared among all types.
* **Delete**: deletes the element and all of it's contents
* **Up/Down arrows**: shifts the element up or down.
* **Element Keyword**: opens the [Element Window](#element-window) to change it's keyword. ***Warning: this can erase the contents of the Element***

## Element Types
* **[Number](#element-number)**: A signed int or signed float, note that source servers are 32-bit.
* **[String](#element-string)**: Generic text, should not contain double-quotes, BluTape adds them on compile when needed.
* **[Selection](#element-selection)**: A choice of several values.
* **[Container](#element-container)**: Something that can contain several other values.

## Element: String
This is a variant of [element](#element) for the String [type](#element-types).
* **Text box**: Large text box for string input, this will have green text.

## Element: Number
This is a variant of [element](#element) for the Number [type](#element-types).
* **Text box**: Small text box for numeric input, this will have blue text.

## Element: Selection
This is a variant of [element](#element) for the Selection [type](#element-types).
* **Selection box**: Dropdown box that can contain several items.

## Element: Container
This is a variant of [element](#element) for the Container [type](#element-types).
* **Edit button**: Accesses the sub-items of the Container, use the [Back button](#stock-menu) to return to the current Element.

## Adding templates to the project
1. Copy the pop file with your templates into.
2. Go to [Template](#template) and click **Reload**.
3. Go to your Root node and add a #base for the added the files.

## Having a default project when starting BluTape
To make a project load on start, simply save a project as "autoload.blu"

## Implementing extra .pop features
If there is a keyword that is not available in BluTape, you can do the following to update it yourself.
1. Close BluTape if it is running.
2. Place a popfile that has this option in datafiles/popfiles.
3. Run update_datafiles.py.
4. Re-launch BluTape.

*This will update datafiles/json/keywords.json to have the new information.*
