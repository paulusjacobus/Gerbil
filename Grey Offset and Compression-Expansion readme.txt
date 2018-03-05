Grey Offset and Compression / Expansion

The Grey Offset value is used to marginally increase or decrease the beginning value that would be the "S" value (PWM) of a G91 gcode.  A negative value will decrease the "S" value making the engraving lighter while a positive number will make the engraving darker.

Compression / Expansion is basicly a percentage of the value derived from the application of the Grey Offset to the original value of "S".  A higher Compression / Expansion value will increase the ultimate "S" value making the engraving darker while a lower Compression / Expansion value will decrease the ultimate "S" value making the engraving lighter.

The formula is essentially 
(Compression Expansion * (255 + Grey offset - original "S" value))

For example:		ex1	ex2	ex3	ex4	ex5	ex6	ex7	ex8	ex9	ex10

original "S" value 	182 	182	182	182	182	182	182	182	182	182
Grey Offset		0 	-5	-10	+5	+10	0	0	0	0	-15
Compression/Expansion	1.0	1.0	1.0	1.0	1.0	.9	.8	1.1	1.2	.7
	equals
new "S" value		73	68	63	78	83	65.69	58.40	80	87.60	40
			
				
in the examples above, ex1 has no adjustments.  ex2 and ex3 reduce the "S" value making the engraving lighter
						ex4 and ex5 increase the "S" value making the engraving darker
						ex6 and ex7 reduce the "S" value making the engraving lighter
						ex8 and ex9 increase the "S" value making the engraving darker
						ex10 is a combination which makes the engraving much lighter

The effect on the engraving is less with the Grey Offset than it is with the Compression / Expansion so adjustments should be made accordingly.  Minor adjustments to lightness or darkness can be done with just the Grey Offset, while more extreme cases of lightness or darkness will most likely need a Compression / Expansion adjustment, possibly in addition the a Grey Offset adjustment.  It's a matter of applying intuition to a trial and error process, but it does save you from needing to adjust $30 values for any but extreme cases.

A good way to start is to make a small version of the image you want to engrave and tinker with these parameters until you are pleased with the engraved resule.  Then expand the image for your full size engraving and run it.

A perfect original could leave these parameters at 0 for Grey offset and 1 for Compression / Expansion thereby having no effect on the engraving.  (If you find one of those perfect originals, please send it to me.)

