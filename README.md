# Gerbil's Inkscape Plug Ins

These Inkscape plug ins have been modified to meet the G-code standard so the can run smoothly in Gerbil's (Grbl) firmware. The engraving Plugin has been modified extensively while the Jtech photonics vector plugin has been only modified slightly (remove the M18 command). You can use these Inkscape plug ins to generate gcode for the basic Grbl Arduino Uno set but the engraving plugin has been modified especially for the customer Gerbil controller to match the Chinese K40 (Stock CO2 laser tube and laser power supply).

First step: Download the Inkscape plugins into your Inkscape/Share/Extensions folder (MAC or Windows)

Second step: Start Inskcape and see if the Plugins turn up under the extensions menu.

- Laser commands being used by Gerbil are:
- Laser On: M4
- Laser Off: M5

Engraving settings for 256 Gray levels:
- Max resolution 382 DPI or 15Pixels/mm with a max speed of 1000mm/min
- Lower resolutions can use higher engraving speed (up to 2000mm/min)

Once the laser head starts sputtering then you know you are driving the controller too hard and reduce its speed.

## Using the Raster Engraving plugin:
- Import a picture from the File, Import menu
- Scale (resize) the canvas in Inkscape to the dimensions of the engraving area you need via "Document properties" ("resize page to content" feature allows you to do this automatically). So, basically your A4 resizes to the engraving size.
- Select the K40 Engraving Plugin from the Extensions menu
- Select the engraving mode "Black and White" or "Gray scale", the levels of Gray (max 256), speed (max 1000 for highest resolution)
- Set the directory (for G-code output files)
- Set the file name
- Hit the generate button (which produces the G-code file into the directory you have configured)

## Using the Vector Cutting Plug in:
The instructions for using of JTech Inkscape plug in can be found here: https://jtechphotonics.com/?page_id=2012

Also this plugin allows engraving via vectors (not rastering) and describes how to combine vector engraving and cutting. The download version on here on Github has been altered: the M18 command has been removed to make it compatible with Grbl.
In inkscape, mirror the Y axis via the button "Flip selected objects horizontally) so that everything looks mirrored in Inkscape and in CNCJS (when uploaded). This is required so the user of the K40 does not have to change their Y axis end stop.
Letter engraving or cutting.
Select the letter tool from inkscape (Big "A" character icon) tools icons on the left vertical bar, write some text on the canvas (Document properties set to "A4, landscape"). Select from top ribbon menu, option "Text", "put on path".  Select from top ribbon menu "Path", "Object to path", select from menu "Extensions", the "Generate G-code/J-Tech Photonics" plugin, generate gcode. Now you can vector engrave or cut letters and numbers (from acrylic for your house and council garbage collection bins!).

## Sending it to the Gerbil Controller
There are two options for sending the generated gcode files to Gerbil: via CNCjs and via streamer.py script.
- Install a G-code sender
- For example https://github.com/cncjs/cncjs or for simple fast install as desktop app (MAC or Windows) https://github.com/cncjs/cncjs/wiki/Desktop-App
- Select Grbl as format
- Select the com port (refresh button at the end of the list dropdown shos the com ports)
- Hit the "Connect" button
- See whether it responds and click on the clear alarms "Unlock" button (on the top/right of the screen)
- See if you can jog the machine via the arrows (set the appropriate step size via "custom" into 10 steps per jog command)
- Upload a raster or vector file (max 10Mb, although can be changed in code)
- Hit the "Play" button in the top bar
- The gcode is now send to Gerbil and you can see the progress on the screen in form of completion and visual movement in the gcode depiction
- The visual reporting bars for the processing queues move. You can change on the fly the F-feed rate, S-Strength of the laser beam, R-receive buffersize. 

Caveat for cncjs: files can be not large unless you change the source code to allow bigger files (limit is configured to 10Mb because the did not envisage the use of this for laser engraving). You can change this in the source code but installation from scratch with maven and node js is a hell. I asked to increase the size which they did for one release and it was back to 10Mb in the next release, sigh.

## Streamer.py for streaming large gcode engraving files to Gerbil

You need to have Python installed on your machine to use it on the command line.
https://www.python.org/downloads/ if you run into issues where the computer MAC or WIndows cannot execute the py script from the command line tool.
Potentially the python script will run because you installed Inkscape which is build on Python.

Cmd Streamer.py <name_of_the_file> <connectedcomport>
For example:
>c:streamer.py name_0001_Gray_256_gcode.txt com1
The comm port can be looked up quickly via CNCjs if you don't know it.
  
Alternatively you can enter streamer.py which shows you the option keys
  
If you stil get python run errors than you might need to install another Python library.
Use the command line tool (MAC or WIN) and type:
>python setup.py install

Now everything should work smoothly!
