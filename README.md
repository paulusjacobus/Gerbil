# Gerbil's Inkscape Plug Ins

These plugs have been modified to meet the G-code standard so the can run in Gerbil's firmware. The engraving Plugin has been modified extensively while the Jtech vector plugin has been only modified slightly (remove the M18 command)

First step: Download the Inkscape plugins into your Inkscape/Share/Extensions folder

Second step: Start Inskcape and see if the Plugins turn up in the extensions menu.

- Laser commands being used by Gerbil are:
- Laser On: M4
- Laser Off: M5

Engraving settings for 256 Gray levels:
- Max resolution 382 DPI or 15Pixels/mm with a max speed of 1000mm/min
- Lower resolutions can use higher engraving speed (upo to 2000mm/min)

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

