# Gerbil's Inkscape Plug Ins

These plugs have been modified to meet the G-code standard so the can run in Gerbil's firmware. The engraving Plugin has been modified extensively while the Jtech vector plugin has been only modified slightly (remove the M18 command)

First step: Download the Inkscape plugins into your Inkscape/Share/Extensions folder

Second step: Start Inskcape and see if the Plugins turn up in the extensions menu.

- Laser commands being used by Gerbil are:
- Laser On: M4
- Laser Off: M5

Engraving settings for 256 Gray levels:
- Max resolution 382 DPI or 15Pixels/mm with a max speed of 1000mm/min
- Lower resolutions can use higher engraving speed (up to 2000mm/min)

Once the laser head starts sputtering you know you are driving the controller too hard and reduce its speed.

## Using the Engraving plugin:
- Import a picture from the File, Import menu
- Scale (resize) the canvas in Inkscape to the dimensions of the engraving via "Document properties"
- Select the K40 Engraving Plugin from the Extensions menu
- Select the engraving mode "Black and White" or "Gray scale", the levels of Gray (max 256), speed (max 1000 for highest resolution)
- Set the directory
- Set the file name

## Using the Cutting Plug in:
The instructions for using of JTech Inkscape plug in can be found here: https://jtechphotonics.com/?page_id=2012

Also this plugin allows engraving via vectors (not rastering) and describes how to combine vector engraving and cutting. The download version on here on Github has been altered: the M18 command has been removed to make it compatible with Grbl.
In inkscape, mirror the Y axis to everything looks mirrored in Inkscape and in CNCJS. THis is done so the user of the K40 does not have to change their Y axis end stop.
Letter engraving or cutting.
Select the letter tool from inkscape (Big A icon) icons on the left vertical bar, write some text on the canvas (Document properties set to A4, landscape). Select from menu option "Text", "put on path".  Select from menu "Path", "Object to path", select from menu "Extensions", the "Generate G-code/J-Tech Photonics" plugin, generate gcode. Now you can cut letters and numbers from acrylic for your house and council garbage collection bins!

## Sending it to the Gerbil Controller

- Install a G-code sender
- For example https://github.com/cncjs/cncjs or for simple fast install as desktop app https://github.com/cncjs/cncjs/wiki/Desktop-App
- Select Grbl as format
- Select the com port
- Connect
- See whether it responds and clcik on the clear alarms "Unlock" button (top/right)
- See if you can jog the machine
- Upload a raster or vector file
- Hit the Play button

Caveat for cncjs: files can be not large unless you change the source code to allow bigger files (limit is configured to 10Mb because the did not envisage the use of this for laser engraving). You can change this in the source code but installation from scratch with maven and node js is a hell. I asked to increase the size which they did for one release and it was back to 10Mb in the next release, sigh.

## Streamer.py for streaming large gcode engraving files to Gerbil

You need to have Python installed on your machine to use it on the command line.
Potentially the python script will run because you installed Inkscape which is build on Python.

Cmd Streamer.py <name_of_the_file> <connectedcomport>
For example:
>c:streamer.py name_0001_Gray_256_gcode.txt com1
