'''
# ----------------------------------------------------------------------------
# Copyright (C) 2014 305engineering <305engineering@gmail.com>
# Original concept by 305engineering.
# Adapted for Grbl Arduino Uno K40 Laser Controller
# awesome.tech
# "THE MODIFIED BEER-WARE LICENSE" (Revision: my own :P):
# <305engineering@gmail.com> wrote this file. As long as you retain this notice you
# can do whatever you want with this stuff (except sell). If we meet some day, 
# and you think this stuff is worth it, you can buy me a beer in return.
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
# BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
# ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# ----------------------------------------------------------------------------
#Change Log
#
#DRG1 - fixed streaking issue when using greyscale
#       added option to modify $30 values
#       Added option to offset from true home at start of engrave
#DRG2 - eliminate negative PWM values
#       added slider to set whitespace bypass speed (from 1000-10000)
#DRG3 - fixed an issue where minimum PWM was not tested resulting in whitestace bypass was not engaged
#       added a slider for minimum PWM value (from 30-100)
#       added this change log
#DRG4 - added return to orig home when x and y offset are in effect
#DRG5 - Added output text file containing parms used for this extension
#DRG6 - Added G54-G59 workspace coordinates
#DRG7 - added code to create a gerbiltemp directory to contain output files when there isn't a valid directory path from the GUI
# ----------------------------------------------------------------------------
'''


import sys
import os
import re

sys.path.append('/usr/share/inkscape/extensions')
sys.path.append('/Applications/Inkscape.app/Contents/Resources/extensions') 

import subprocess
import math

import inkex
import png
import array
#streamer part
import time
import serial
import glob

import datetime #DRG5

#ser = 0
class GcodeExport(inkex.Effect):

######## 	Richiamata da _main()
	def __init__(self):
		"""init the effetc library and get options from gui"""
		inkex.Effect.__init__(self)
		
		# Opzioni di esportazione dell'immagine
		self.OptionParser.add_option("-d", "--directory",action="store", type="string", dest="directory", default="/home/",help="Directory for files") ####check_dir
		self.OptionParser.add_option("-f", "--filename", action="store", type="string", dest="filename", default="-1.0", help="File name")            
		self.OptionParser.add_option("","--add-numeric-suffix-to-filename", action="store", type="inkbool", dest="add_numeric_suffix_to_filename", default=True,help="Add numeric suffix to filename")            
		self.OptionParser.add_option("","--bg_color",action="store",type="string",dest="bg_color",default="",help="")
		self.OptionParser.add_option("","--resolution",action="store", type="int", dest="resolution", default="5",help="") #Usare il valore su float(xy)/resolution e un case per i DPI dell export
		
		
		# Come convertire in scala di grigi
		self.OptionParser.add_option("","--grayscale_type",action="store", type="int", dest="grayscale_type", default="1",help="") 
		
		# Modalita di conversione in Bianco e Nero 
		self.OptionParser.add_option("","--conversion_type",action="store", type="int", dest="conversion_type", default="1",help="") 
		
		# Opzioni modalita 
		self.OptionParser.add_option("","--BW_threshold",action="store", type="int", dest="BW_threshold", default="128",help="") 
		self.OptionParser.add_option("","--BWBlackvalue",action="store", type="int", dest="BWBlackvalue", default="254",help="") 
		self.OptionParser.add_option("","--Grey_multiplier",action="store", type="float", dest="Grey_multiplier", default="1.0",help="") 
		self.OptionParser.add_option("","--Grey_offset",action="store", type="int", dest="Grey_offset", default="0",help="") 
		self.OptionParser.add_option("","--grayscale_resolution",action="store", type="int", dest="grayscale_resolution", default="1",help="") 
		
		#Velocita Nero e spostamento
		self.OptionParser.add_option("","--speed_ON",action="store", type="int", dest="speed_ON", default="200",help="")
		self.OptionParser.add_option("", "--speedupmsg",action="store", type="string", dest="speedupmsg", default="",help="Acceleration for bupassing whitespace msg") #DRG2
		self.OptionParser.add_option("","--speedup",action="store", type="string", dest="speedup", default="3000",help="") #DRG2
		self.OptionParser.add_option("", "--minPWMmsg",action="store", type="string", dest="minPWMmsg", default="",help="Acceleration for bypassing whitespace msg") #DRG3
		self.OptionParser.add_option("","--minPWM",action="store", type="int", dest="minPWM", default="70",help="") #DRG3

                # $30 Value  DRG1
		self.OptionParser.add_option("","--30_Value",action="store", type="int", dest="PWM_Value", default="1000",help="$30 value") #DRG1
		self.OptionParser.add_option("","--change30",action="store", type="inkbool", dest="change30", default=False,help="whether to send $30") #DRG1
		self.OptionParser.add_option("", "--30warn",action="store", type="string", dest="set30", default="30warn",help="$30 caution message will be modified below") #DRG1
		self.OptionParser.add_option("", "--tab",action="store", type="string", dest="tab", default="/page_1/",help="The active tab when Apply was pressed") #DRG1

		# Mirror Y
		self.OptionParser.add_option("","--flip_y",action="store", type="inkbool", dest="flip_y", default=False,help="")
		
		# Homing
		self.OptionParser.add_option("","--homing",action="store", type="int", dest="homing", default="1",help="")

		# G54 - G59 Workspace Coordinates DRG5
		self.OptionParser.add_option("","--g54_value",action="store", type="int", dest="g54_value", default="0",help="Workspace Coordinates") #DRG5
		self.OptionParser.add_option("", "--g54_msg",action="store", type="string", dest="g54_msg", default="g54_msg",help="G54 message")  #DRG5

		
		# Offset
		self.OptionParser.add_option("","--offset",action="store", type="inkbool", dest="offset", default=False,help="Offset")
		self.OptionParser.add_option("", "--offsetd",action="store", type="string", dest="offsetd", default="offsetd",help="Offset description")  #DRG1
		self.OptionParser.add_option("","--xoffset",action="store", type="string", dest="xoffset", default="0.0", help="X offset from zero")
		self.OptionParser.add_option("","--yoffset",action="store", type="string", dest="yoffset", default="0.0", help="Y offset from zero")
		
		
		# Commands
		self.OptionParser.add_option("","--laseron", action="store", type="string", dest="laseron", default="M4", help="")
		self.OptionParser.add_option("","--laseroff", action="store", type="string", dest="laseroff", default="M3", help="")
		
		# Anteprima = Solo immagine BN 
		self.OptionParser.add_option("","--preview_only",action="store", type="inkbool", dest="preview_only", default=False,help="") 
		self.OptionParser.add_option("","--stream",action="store", type="inkbool", dest="stream", default=False,help="")
		self.OptionParser.add_option("","--streaming",action="store", type="string", dest="streaming", default="1",help="")
		#inkex.errormsg("BLA BLA BLA Messaggio da visualizzare") #DEBUG

		global run_start_time #DRG5
		run_start_time = time.strftime('%X %x') #DRG5
		global begin_time #DRG5
		begin_time = time.time() #DRG5
          
######## 	Richiamata da __init__()
########	Qui si svolge tutto
	def effect(self):
		

		current_file = self.args[-1]
		bg_color = self.options.bg_color
		
		
		
		##Implementare check_dir
		
		if (os.path.isdir(self.options.directory)) == False: #DRG7
			if sys.platform.startswith('win'): #DRG7
				self.options.directory = 'C:\gerbiltemp' #DRG7
			else: #DRG7
				self.options.directory = '/gerbiltemp' #DRG7
			if (os.path.isdir(self.options.directory)) == False: #DRG7
				os.mkdir(self.options.directory) #DRG7
			inkex.debug("The directory you specified does not exist - using " + self.options.directory + " instead") #DRG7
			
                ##CODICE SE ESISTE LA DIRECTORY
                #inkex.errormsg("OK") #DEBUG

                
                #Aggiungo un suffisso al nomefile per non sovrascrivere dei file
		if self.options.add_numeric_suffix_to_filename :
			dir_list = os.listdir(self.options.directory) #List di tutti i file nella directory di lavoro
			temp_name =  self.options.filename
			max_n = 0
			for s in dir_list :
				r = re.match(r"^%s_0*(\d+)%s$"%(re.escape(temp_name),'.png' ), s)
				if r :
					max_n = max(max_n,int(r.group(1)))      
			self.options.filename = temp_name + "_" + ( "0"*(4-len(str(max_n+1))) + str(max_n+1) )


		#genero i percorsi file da usare
		
		suffix = ""
		if self.options.conversion_type == 1:
			suffix = "_BWfix_"+str(self.options.BW_threshold)+"_"
		elif self.options.conversion_type == 2:
			suffix = "_BWrnd_"
		elif self.options.conversion_type == 3:
			suffix = "_H_"
		elif self.options.conversion_type == 4:
			suffix = "_Hrow_"
		elif self.options.conversion_type == 5:
			suffix = "_Hcol_"
		else:
			if self.options.grayscale_resolution == 1:
				suffix = "_Gray_256_"
			elif self.options.grayscale_resolution == 2:
				suffix = "_Gray_128_"
			elif self.options.grayscale_resolution == 4:
				suffix = "_Gray_64_"
			elif self.options.grayscale_resolution == 8:
				suffix = "_Gray_32_"
			elif self.options.grayscale_resolution == 16:
				suffix = "_Gray_16_"
			elif self.options.grayscale_resolution == 32:
				suffix = "_Gray_8_"
			else:
				suffix = "_Gray_"
			
		
		pos_file_png_exported = os.path.join(self.options.directory,self.options.filename+".png") 
		pos_file_png_BW = os.path.join(self.options.directory,self.options.filename+suffix+"preview.png") 
		pos_file_gcode = os.path.join(self.options.directory,self.options.filename+suffix+"gcode.txt") 
		pos_file_log = os.path.join(self.options.directory,self.options.filename+suffix+"gcode.log")
		pos_file_parms = os.path.join(self.options.directory,self.options.filename+suffix+"parms.txt") #DRG5                    
					

		#Esporto l'immagine in PNG
		self.exportPage(pos_file_png_exported,current_file,bg_color)

		
		#DA FARE
		#Manipolo l'immagine PNG per generare il file Gcode
		self.PNGtoGcode(pos_file_png_exported,pos_file_png_BW,pos_file_gcode)
		#list the available ports
		#port = self.serial_ports()
		#stream the gcode to Gerbil
		if self.options.streaming == "3" :
			try:
				port = self.serial_ports()
				flag = True
			except:
				inkex.errormsg(_("No Serial port found with controller " ) )
				flag = False
			if flag == True : 
				self.GcodetoController(port,pos_file_gcode,pos_file_log,pos_file_parms) #DRG5
		#DRG7 else:
			#DRG7 inkex.errormsg("Directory does not exist! Please specify existing directory!")

	
		
            
            
########	ESPORTA L IMMAGINE IN PNG		
######## 	Richiamata da effect()
		
	def exportPage(self,pos_file_png_exported,current_file,bg_color):		
		######## CREAZIONE DEL FILE PNG ########
		#Crea l'immagine dentro la cartella indicata  da "pos_file_png_exported"
		# -d 127 = risoluzione 127DPI  =>  5 pixel/mm  1pixel = 0.2mm
		###command="inkscape -C -e \"%s\" -b\"%s\" %s -d 127" % (pos_file_png_exported,bg_color,current_file) 

		if self.options.resolution == 1:
			DPI = 25.4
		elif self.options.resolution == 2:
			DPI = 50.8
		elif self.options.resolution == 5:
			DPI = 127
		elif self.options.resolution == 10:
			DPI = 254
		else:
			DPI = 381 #254 15 pixels

		command="inkscape -C -e \"%s\" -b\"%s\" %s -d %s" % (pos_file_png_exported,bg_color,current_file,DPI) #Comando da linea di comando per esportare in PNG
					
		p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		return_code = p.wait()
		f = p.stdout
		err = p.stderr


########	CREA IMMAGINE IN B/N E POI GENERA GCODE
######## 	Richiamata da effect()

	def PNGtoGcode(self,pos_file_png_exported,pos_file_png_BW,pos_file_gcode):
		
		######## GENERO IMMAGINE IN SCALA DI GRIGI ########
		#Scorro l immagine e la faccio diventare una matrice composta da list


		reader = png.Reader(pos_file_png_exported)#File PNG generato
		
		w, h, pixels, metadata = reader.read_flat()
		
		#matrice = [[255 for i in range(w)]for j in range(h)]  #List al posto di un array
		matrice = [[382 for i in range(w)]for j in range(h)] 

		#Scrivo una nuova immagine in Scala di grigio 8bit
		#copia pixel per pixel 
		
		if self.options.grayscale_type == 1:
			#0.21R + 0.71G + 0.07B
			for y in range(h): # y varia da 0 a h-1
				for x in range(w): # x varia da 0 a w-1
					pixel_position = (x + y * w)*4 if metadata['alpha'] else (x + y * w)*3
					matrice[y][x] = int(pixels[pixel_position]*0.21 + pixels[(pixel_position+1)]*0.71 + pixels[(pixel_position+2)]*0.07) #matrice[y][x] = int(pixels[pixel_position]*0.21 + pixels[(pixel_position+1)]*0.71 + pixels[(pixel_position+2)]*0.07)
		
		elif self.options.grayscale_type == 2:
			#(R+G+B)/3
			for y in range(h): # y varia da 0 a h-1
				for x in range(w): # x varia da 0 a w-1
					pixel_position = (x + y * w)*4 if metadata['alpha'] else (x + y * w)*3
					matrice[y][x] = int((pixels[pixel_position] + pixels[(pixel_position+1)]+ pixels[(pixel_position+2)]) / 3 )		

		elif self.options.grayscale_type == 3:
			#R
			for y in range(h): # y varia da 0 a h-1
				for x in range(w): # x varia da 0 a w-1
					pixel_position = (x + y * w)*4 if metadata['alpha'] else (x + y * w)*3
					matrice[y][x] = int(pixels[pixel_position])			

		elif self.options.grayscale_type == 4:
			#G
			for y in range(h): # y varia da 0 a h-1
				for x in range(w): # x varia da 0 a w-1
					pixel_position = (x + y * w)*4 if metadata['alpha'] else (x + y * w)*3
					matrice[y][x] = int(pixels[(pixel_position+1)])	
		
		elif self.options.grayscale_type == 5:
			#B
			for y in range(h): # y varia da 0 a h-1
				for x in range(w): # x varia da 0 a w-1
					pixel_position = (x + y * w)*4 if metadata['alpha'] else (x + y * w)*3
					matrice[y][x] = int(pixels[(pixel_position+2)])				
			
		elif self.options.grayscale_type == 6:
			#Max Color
			for y in range(h): # y varia da 0 a h-1
				for x in range(w): # x varia da 0 a w-1
					pixel_position = (x + y * w)*4 if metadata['alpha'] else (x + y * w)*3
					list_RGB = pixels[pixel_position] , pixels[(pixel_position+1)] , pixels[(pixel_position+2)]
					matrice[y][x] = int(max(list_RGB))				

		else:
			#Min Color
			for y in range(h): # y varia da 0 a h-1
				for x in range(w): # x varia da 0 a w-1
					pixel_position = (x + y * w)*4 if metadata['alpha'] else (x + y * w)*3
					list_RGB = pixels[pixel_position] , pixels[(pixel_position+1)] , pixels[(pixel_position+2)]
					matrice[y][x] = int(min(list_RGB))	
		

		####Ora matrice contiene l'immagine in scala di grigi


		######## GENERO IMMAGINE IN BIANCO E NERO ########
		#Scorro matrice e genero matrice_BN
		B=255
		N=255-self.options.BWBlackvalue
		
		matrice_BN = [[255 for i in range(w)]for j in range(h)]
		
		
		if self.options.conversion_type == 1:
			#B/W fixed threshold
			soglia = self.options.BW_threshold
			for y in range(h): 
				for x in range(w):
					if matrice[y][x] >= soglia :
						matrice_BN[y][x] = B
					else:
						matrice_BN[y][x] = N
	
			
		elif self.options.conversion_type == 2:
			#B/W random threshold
			from random import randint
			for y in range(h): 
				for x in range(w): 
					soglia = randint(20,235)
					if matrice[y][x] >= soglia :
						matrice_BN[y][x] = B
					else:
						matrice_BN[y][x] = N
			
			
		elif self.options.conversion_type == 3:
			#Halftone
			Step1 = [[B,B,B,B,B],[B,B,B,B,B],[B,B,N,B,B],[B,B,B,B,B],[B,B,B,B,B]]
			Step2 = [[B,B,B,B,B],[B,B,N,B,B],[B,N,N,N,B],[B,B,N,B,B],[B,B,B,B,B]]
			Step3 = [[B,B,N,B,B],[B,N,N,N,B],[N,N,N,N,N],[B,N,N,N,B],[B,B,N,B,B]]
			Step4 = [[B,N,N,N,B],[N,N,N,N,N],[N,N,N,N,N],[N,N,N,N,N],[B,N,N,N,B]]
			
			for y in range(h/5): 
				for x in range(w/5): 
					media = 0
					for y2 in range(5):
						for x2 in range(5):
							media +=  matrice[y*5+y2][x*5+x2]
					media = media /25
					for y3 in range(5):
						for x3 in range(5):
							if media >= 250 and media <= 255:
								matrice_BN[y*5+y3][x*5+x3] = 	B	
							if media >= 190 and media < 250:
								matrice_BN[y*5+y3][x*5+x3] =	Step1[y3][x3]
							if media >= 130 and media < 190:
								matrice_BN[y*5+y3][x*5+x3] =	Step2[y3][x3]
							if media >= 70 and media < 130:
								matrice_BN[y*5+y3][x*5+x3] =	Step3[y3][x3]
							if media >= 10 and media < 70:
								matrice_BN[y*5+y3][x*5+x3] =	Step4[y3][x3]		
							if media >= 0 and media < 10:
								matrice_BN[y*5+y3][x*5+x3] = N


		elif self.options.conversion_type == 4:
			#Halftone row
			Step1r = [B,B,N,B,B]
			Step2r = [B,N,N,B,B]
			Step3r = [B,N,N,N,B]
			Step4r = [N,N,N,N,B]

			for y in range(h): 
				for x in range(w/5): 
					media = 0
					for x2 in range(5):
						media +=  matrice[y][x*5+x2]
					media = media /5
					for x3 in range(5):
						if media >= 250 and media <= 255:
							matrice_BN[y][x*5+x3] = 	B
						if media >= 190 and media < 250:
							matrice_BN[y][x*5+x3] =	Step1r[x3]
						if media >= 130 and media < 190:
							matrice_BN[y][x*5+x3] =	Step2r[x3]
						if media >= 70 and media < 130:
							matrice_BN[y][x*5+x3] =	Step3r[x3]
						if media >= 10 and media < 70:
							matrice_BN[y][x*5+x3] =	Step4r[x3]		
						if media >= 0 and media < 10:
							matrice_BN[y][x*5+x3] = N			


		elif self.options.conversion_type == 5:
			#Halftone column
			Step1c = [B,B,N,B,B]
			Step2c = [B,N,N,B,B]
			Step3c = [B,N,N,N,B]
			Step4c = [N,N,N,N,B]

			for y in range(h/5):
				for x in range(w):
					media = 0
					for y2 in range(5):
						media +=  matrice[y*5+y2][x]
					media = media /5
					for y3 in range(5):
						if media >= 250 and media <= 255:
							matrice_BN[y*5+y3][x] = 	B
						if media >= 190 and media < 250:
							matrice_BN[y*5+y3][x] =	Step1c[y3]
						if media >= 130 and media < 190:
							matrice_BN[y*5+y3][x] =	Step2c[y3]
						if media >= 70 and media < 130:
							matrice_BN[y*5+y3][x] =	Step3c[y3]
						if media >= 10 and media < 70:
							matrice_BN[y*5+y3][x] =	Step4c[y3]		
						if media >= 0 and media < 10:
							matrice_BN[y*5+y3][x] = N			
			
		else:
			#Grayscale
			if self.options.grayscale_resolution == 1:
				matrice_BN = matrice
			else:
				for y in range(h): 
					for x in range(w): 
						if matrice[y][x] <= 0:
							matrice_BN[y][x] == 0
							
						if matrice[y][x] >= 255:
							matrice_BN[y][x] == 255
						
						if matrice[y][x] >= 0 and matrice[y][x] <255:
							matrice_BN[y][x] = ( matrice[y][x] // self.options.grayscale_resolution ) * self.options.grayscale_resolution
							#matrice_BN[y][x] = (( matrice_BN[y][x] - 70 ) * 1.3)
			
			
		####Ora matrice_BN contiene l'immagine in Bianco (255) e Nero (0)


		#### SALVO IMMAGINE IN BIANCO E NERO ####
		file_img_BN = open(pos_file_png_BW, 'wb') #Creo il file
		Costruttore_img = png.Writer(w, h, greyscale=True, bitdepth=8) #Impostazione del file immagine
		Costruttore_img.write(file_img_BN, matrice_BN) #Costruttore del file immagine
		file_img_BN.close()	#Chiudo il file


		#### GENERO IL FILE GCODE ####
		if self.options.streaming != "1": #Genero Gcode solo se devo
		
			if self.options.flip_y == False: #Inverto asse Y solo se flip_y = False     
				#-> coordinate Cartesiane (False) Coordinate "informatiche" (True)
				matrice_BN.reverse()				

			
			Laser_ON = False
			#F_G01 = self.options.speed_ON
			Scala = self.options.resolution

			F_G01 = self.options.speed_ON
			F_G00 = self.options.speedup #acceleration to bypass whitespace DRG2
			#DRG2 F_G00 = '3000' #travel speed
			S_PWM = '0'  #DRG2
			file_gcode = open(pos_file_gcode, 'w')  #Creo il file
			
			#Configurazioni iniziali standard Gcode
			file_gcode.write('; Generated with:\n; "Grbl compatible Raster2LaserGcode generator"\n; by 305 Engineering and Awesome.tech\n; Modified for K40Controller\n;\n;\n')
			#HOMING
			file_gcode.write('$X\n')			

			if self.options.homing == 1:
				file_gcode.write('$H\n')
			elif self.options.homing == 2:
				file_gcode.write('G0 X0 Y0\n')			
			else:
				pass

			if self.options.g54_value != 0: #DRG6
				if self.options.g54_value == 1: #DRG6
					file_gcode.write('G55 G0 X0 Y0 \n') #DRG6
				elif self.options.g54_value == 2: #DRG6
					file_gcode.write('G56 G0 X0 Y0 \n') #DRG6
				elif self.options.g54_value == 3: #DRG6
					file_gcode.write('G57 G0 X0 Y0 \n') #DRG6
				elif self.options.g54_value == 4: #DRG6
					file_gcode.write('G58 G0 X0 Y0 \n') #DRG6
				elif self.options.g54_value == 5: #DRG6
					file_gcode.write('G59 G0 X0 Y0 \n') #DRG6
			else: #DRG6
				if self.options.offset == True: #DRG6
					file_gcode.write('G0 X+' + self.options.xoffset + ' Y+' + self.options.yoffset + '\n') #DRG1 DRG4 DRG6
				#DRG1 file_gcode.write('G0 X-' + self.options.xoffset + ' Y-' + self.options.yoffset + ' \n')
				#file_gcode.write('G90\n')
				else: #DRG6
					pass #DRG6
			if self.options.change30 == True:  #DRG1
				self.options.set30=('$30=' + str(self.options.PWM_Value) +'\n')  #DRG1				
			else:  #DRG1
				self.options.set30 = 'S0\n'	#DRG1	
			file_gcode.write('G21\n')			
			file_gcode.write('G90\n')
			file_gcode.write('G92 X0.0 Y0.0\n')
			file_gcode.write(self.options.laseron +'\n')
			
			#file_gcode.write(self.options.set30)  #DRG1 Temp debug code
	
			#Creazione del Gcode
			
			#allargo la matrice per lavorare su tutta l'immagine
			for y in range(h):
				matrice_BN[y].append(B)
			w = w+1
			
			if self.options.conversion_type != 6:
				for y in range(h):
					if y % 2 == 0 :
						for x in range(w):
							if matrice_BN[y][x] == N :
								if Laser_ON == False :
									#file_gcode.write('G00 X' + str(float(x)/Scala) + ' Y' + str(float(y)/Scala) + ' F' + str(F_G00) + '\n')
									file_gcode.write('G0 X' + str(round((float(x)/Scala),2)) + ' Y' + str(round((float(y)/Scala),2)) + ' F' + str(F_G00) + ' S0 \n') #tolto il Feed sul G00
									#file_gcode.write(self.options.laseron + '\n')			
									Laser_ON = True
								if  Laser_ON == True :   #DEVO evitare di uscire dalla matrice
									if x == w-1 :
										file_gcode.write('G1X' + str(round((float(x)/Scala),2)) + 'Y' + str(round((float(y)/Scala),2)) +' F' + str(F_G01) + ' S' + str(255 - matrice_BN[y][x]) + '\n')
										#file_gcode.write(self.options.laseroff + '\n')
										Laser_ON = False
									else: 
										if matrice_BN[y][x+1] != N :
											file_gcode.write('G1X' + str(round((float(x)/Scala),2)) + 'Y' + str(round((float(y)/Scala),2)) + ' F' + str(F_G01) + ' S' + str(255 - matrice_BN[y][x]) + '\n')
											#file_gcode.write(self.options.laseroff + '\n')
											Laser_ON = False
					else:
						for x in reversed(range(w)):
							if matrice_BN[y][x] == N :
								if Laser_ON == False :
									#file_gcode.write('G00 X' + str(float(x)/Scala) + ' Y' + str(float(y)/Scala) + ' F' + str(F_G00) + '\n')
									file_gcode.write('G0X' + str(round((float(x)/Scala),2)) + 'Y' + str(round((float(y)/Scala),2)) + ' F' + str(F_G00) + ' S0 \n') #tolto il Feed sul G00
									#file_gcode.write(self.options.laseron + '\n')			
									Laser_ON = True
								if  Laser_ON == True :   #DEVO evitare di uscire dalla matrice
									if x == 0 :
										file_gcode.write('G1X' + str(round((float(x)/Scala),2)) + 'Y' + str(round((float(y)/Scala),2)) +' F' + str(F_G01) + ' S' + str(255 - matrice_BN[y][x]) + '\n')
										#file_gcode.write(self.options.laseroff + '\n')
										Laser_ON = False
									else: 
										if matrice_BN[y][x-1] != N :
											file_gcode.write('G1X' + str(round((float(x)/Scala),2)) + 'Y' + str(round((float(y)/Scala),2)) + ' F' + str(F_G01) + ' S' + str(255 - matrice_BN[y][x]) + '\n')
											#file_gcode.write(self.options.laseroff + '\n')
											Laser_ON = False				

			else: ##SCALA in Grey
				for y in range(h):
					if y % 2 == 0 :
						for x in range(w):
							S_PWM = self.options.Grey_multiplier*(255 + self.options.Grey_offset - matrice_BN[y][x])  #DRG2
							if S_PWM > 0:  #DRG2
								pass  #DRG2
							elif S_PWM == 0:  #DRG2
								pass  #DRG2
							else:  #DRG2
								S_PWM = 0  #DRG2
							if matrice_BN[y][x] != B :
								if Laser_ON == False :
									#Y axis move, no lasering
									file_gcode.write('G0 X' + str(round((float(x)/Scala),2)) + ' Y' + str(round((float(y)/Scala),2))  + ' F' + str(F_G00) + ' S0' + '\n') #DRG1
									#DRG1 file_gcode.write('G1 X' + str(round((float(x)/Scala),2)) + ' Y' + str(round((float(y)/Scala),2))  + ' F' + str(F_G00) + '\n')
									#file_gcode.write(self.options.laseron + '\n')
									Laser_ON = True
									
								if  Laser_ON == True :   #DEVO evitare di uscire dalla matrice
									if x == w-1 : #end of line check stop lasering
										file_gcode.write('G1X' + str(round((float(x)/Scala),2)) + 'Y' + str(round((float(y)/Scala),2)) +' F' + str(F_G01) + ' S' + str(S_PWM) + '\n') #DRG3
										#DRG1 file_gcode.write('G1X' + str(round((float(x)/Scala),2)) + 'Y' + str(round((float(y)/Scala),2)) +' F' + str(F_G00) + '\n')
										#file_gcode.write(self.options.laseroff + '\n')
										Laser_ON = False
										
									else: 
										if matrice_BN[y][x+1] == B:
											if S_PWM >= self.options.minPWM: #DRG3
												file_gcode.write('G1X' + str(round((float(x+1)/Scala),2)) + 'Y' + str(round((float(y)/Scala),2)) + ' F' + str(F_G01) + ' S' + str(S_PWM) +'\n') #DRG2 #DRG3
												Laser_ON = False #DRG3
												#DRG2 file_gcode.write('G1X' + str(round((float(x+1)/Scala),2)) + 'Y' + str(round((float(y)/Scala),2)) + ' F' + str(F_G01) + ' S' + str(self.options.Grey_multiplier*(255 + self.options.Grey_offset - matrice_BN[y][x])) +'\n') #was x+1
												#file_gcode.write(self.options.laseron + '\n')                                                                                          
											else:
												file_gcode.write('G1X' + str(round((float(x+1)/Scala),2)) + 'Y' + str(round((float(y)/Scala),2)) + ' F' + str(F_G00) + ' S0' +'\n') #DRG2 #DRG3
												Laser_ON = False #DRG3
												#DRG1 else : file_gcode.write('G1X' + str(round((float(x+1)/Scala),2)) + 'Y' + str(round((float(y)/Scala),2)) + ' F' + str(F_G00) + ' S' + str(self.options.Grey_multiplier*(255 + self.options.Grey_offset - matrice_BN[y][x])) +'\n') #was x+1
												#file_gcode.write(self.options.laseron + '\n')                                                                                                                                                                               
										elif matrice_BN[y][x] != matrice_BN[y][x+1] :
											if S_PWM >= self.options.minPWM: #DRG3
												file_gcode.write('G1X' + str(round((float(x+1)/Scala),2)) + 'Y' + str(round((float(y)/Scala),2)) + ' F' + str(F_G01) + ' S' + str(S_PWM) +'\n') #DRG2 #DRG3
												#DRG2 file_gcode.write('G1X' + str(round((float(x+1)/Scala),2)) + 'Y' + str(round((float(y)/Scala),2)) + ' F' + str(F_G01) + ' S' + str(self.options.Grey_multiplier*(255 + self.options.Grey_offset - matrice_BN[y][x])) +'\n') #was x+1
												#file_gcode.write(self.options.laseron + '\n')												
											else:
												file_gcode.write('G1X' + str(round((float(x+1)/Scala),2)) + 'Y' + str(round((float(y)/Scala),2)) + ' F' + str(F_G00) + ' S0' +'\n') #DRG1 ##DRG3
												#DRG1 else : file_gcode.write('G1X' + str(round((float(x+1)/Scala),2)) + 'Y' + str(round((float(y)/Scala),2)) + ' F' + str(F_G00) + ' S' + str(self.options.Grey_multiplier*(255 + self.options.Grey_offset - matrice_BN[y][x])) +'\n') #was x+1
												#file_gcode.write(self.options.laseron + '\n')
											
					
					else:
						for x in reversed(range(w)):
							S_PWM = self.options.Grey_multiplier*(255 + self.options.Grey_offset - matrice_BN[y][x])  #DRG2
							if S_PWM > 0:  #DRG2
								pass  #DRG2
							elif S_PWM == 0:  #DRG2
								pass  #DRG2
							else:  #DRG2
								S_PWM = 0  #DRG2
							if matrice_BN[y][x] != B :
								if Laser_ON == False :
									#Y axis move no lavering
									file_gcode.write('G0X' + str(round((float(x+1)/Scala),2)) + ' Y' + str(round((float(y)/Scala),2))  + ' F' + str(F_G00) + ' S0' + '\n') #DRG1 #DRG3
									#DRG1 file_gcode.write('G1 X' + str(round((float(x+1)/Scala),2)) + ' Y' + str(round((float(y)/Scala),2))  + ' F' + str(F_G00) + ' \n')
									#file_gcode.write(self.options.laseron +'\n')
									Laser_ON = True
									
								if  Laser_ON == True :   #DEVO evitare di uscire dalla matrice
									if x == 0 : #return line end check stop lasering
										file_gcode.write('G0X' + str(round((float(x)/Scala),2)) + 'Y' + str(round((float(y)/Scala),2)) +' F' + str(F_G00) + ' S0' + '\n') #DRG1
										#DRG1 file_gcode.write('G1X' + str(round((float(x)/Scala),2)) + 'Y' + str(round((float(y)/Scala),2)) +' F' + str(F_G01) + '\n')
										#file_gcode.write(self.options.laseroff + '\n')
										Laser_ON = False
										
									else: 
										if matrice_BN[y][x-1] == B:
											if S_PWM >= self.options.minPWM: #DRG3
												file_gcode.write('G1X' + str(round((float(x)/Scala),2)) + 'Y' + str(round((float(y)/Scala),2)) + ' F' + str(F_G01) + ' S' + str(S_PWM) + '\n') #DRG2 #DRG3
												Laser_ON = False #DRG3
												#drg2 file_gcode.write('G1X' + str(round((float(x)/Scala),2)) + 'Y' + str(round((float(y)/Scala),2)) + ' F' + str(F_G01) + ' S' + str(self.options.Grey_multiplier*(255 + self.options.Grey_offset - matrice_BN[y][x])) +'\n') # was x-1
												#file_gcode.write(self.options.laseron +'\n')												
											else:
												file_gcode.write('G1X' + str(round((float(x+1)/Scala),2)) + 'Y' + str(round((float(y)/Scala),2)) + ' F' + str(F_G00) + ' S0' +'\n') #DRG2 #DRG3
												Laser_ON = False #DRG3
												#DRG1 else : file_gcode.write('G1X' + str(round((float(x)/Scala),2)) + 'Y' + str(round((float(y)/Scala),2)) + ' F' + str(F_G00) + ' S' + str(self.options.Grey_multiplier*(255 + self.options.Grey_offset - matrice_BN[y][x])) +'\n') # was x-1
												#file_gcode.write(self.options.laseron +'\n')
																																		
										elif  matrice_BN[y][x] != matrice_BN[y][x-1] :
											if S_PWM >= self.options.minPWM: #DRG3
												file_gcode.write('G1X' + str(round((float(x)/Scala),2)) + 'Y' + str(round((float(y)/Scala),2)) + ' F' + str(F_G01) + ' S' + str(S_PWM) + '\n') #DRG2 #DRG3
												#drg2 file_gcode.write('G1X' + str(round((float(x)/Scala),2)) + 'Y' + str(round((float(y)/Scala),2)) + ' F' + str(F_G01) + ' S' + str(self.options.Grey_multiplier*(255 + self.options.Grey_offset - matrice_BN[y][x])) +'\n') # was x-1
												#file_gcode.write(self.options.laseron +'\n')
												
											else:
												file_gcode.write('G1X' + str(round((float(x)/Scala),2)) + 'Y' + str(round((float(y)/Scala),2)) + ' F' + str(F_G00) + ' S0' +'\n') #DRG1 #DRG3
												#DRG1 else : file_gcode.write('G1X' + str(round((float(x)/Scala),2)) + 'Y' + str(round((float(y)/Scala),2)) + ' F' + str(F_G00) + ' S' + str(self.options.Grey_multiplier*(255 + self.options.Grey_offset - matrice_BN[y][x])) +'\n') # was x-1
												#file_gcode.write(self.options.laseron +'\n')
											
			
			
			#Configure final standard Gcode
			file_gcode.write(self.options.laseroff + '\n')
			file_gcode.write('S0\n')
			if self.options.g54_value != 0: #DRG6
				file_gcode.write('G54 G0 X0 Y0') #DRG6
			elif self.options.offset == True: #DRG4 DRG6
				file_gcode.write('G0 X-' + self.options.xoffset + ' Y-' + self.options.yoffset + '\n') #DRG4 DRG6
			else: #DRG4 DRG6
				file_gcode.write('G0 X0 Y0\n') #DRG4
			#HOMING
			# if self.options.homing == 1:
				# file_gcode.write('$H\n')
			# else:
				# pass
			
			file_gcode.close() #Close the file
			
	def GcodetoController(self,port,pos_file_gcode,pos_file_log,pos_file_parms): #DRG5
		#streaming code start

		RX_BUFFER_SIZE = 128 #128
		BAUD_RATE = 115200
		ENABLE_STATUS_REPORTS = True
		REPORT_INTERVAL = 1.0 # seconds

		is_run = True # Controls query timer
		global set30

		verbose = False
		settings_mode = False
		check_mode = False
		f = open(pos_file_gcode, 'r')
		if verbose :
			log = open(pos_file_log, 'w')			
		# Initialize
		try:
			s = serial.Serial(port[0],BAUD_RATE)
			s.writeTimeout = 2.0   #DRG1
			s.timeout = 2.0   #DRG1	
			s.flushInput()
			s.flushOutput()
			#print "Initializing Grbl..."
			s.write("\r\n\r\n")			
			# Wait for grbl to initialize and flush startup text in serial input
			#time.sleep(3)
			#s.write("$X\n")
			time.sleep(3.0)
			s.flushInput()
			s.write(self.options.set30)    #DRG1
			#s.write('\$\n')   #DRG1
			time.sleep(3.0)   #DRG1
			s.flushInput()   #DRG1
			start_time = time.time();
			# Stream g-code to grbl
			l_count = 0
			error_count = 0
			out_temp = 0
			g_count = 0
			c_line = []
			for line in f:
				l_count += 1 # Iterate line counter
				#l_block = re.sub('\s|\(.*?\)','',line).upper() # Strip comments/spaces/new line and capitalize
				l_block = line.strip()
				c_line.append(len(l_block)+1) # Track number of characters in grbl serial read buffer
				grbl_out = '' 
				while sum(c_line) >= RX_BUFFER_SIZE-1 | s.inWaiting() :
					try :
						out_temp = s.readline().strip() # Wait for grbl response
						#time.sleep(0.2)
					except :
						if verbose : log.write("\nG-code block read error!")
						pass
					if out_temp.find('ok') < 0 and out_temp.find('error') < 0 :
						#s.flushInput()
						if verbose : log.write ( "    MSG: not Ok/Error \""+out_temp+"\"") # Debug response
					else :
						if out_temp.find('error') >= 0 or out_temp == 0 : 
							error_count += 1
							if verbose : log.write("\n Error rate "+ str(error_count))
						g_count += 1 # Iterate g-code counter
						if verbose: log.write( "  REC<"+str(g_count)+": \""+out_temp+"\"")
						#if l_block > 0 :
						if verbose : log.write("\n c_line array sum "+str(sum(c_line)))
						del c_line[0] # Delete the block character count corresponding to the last 'ok'
				try:
					#time.sleep(.1)
					s.write(l_block + '\n') # Send g-code block to grbl
				except:
					if verbose : log.write("\nG-code block comm erroGcodetoControllerr!")
					s.close()
					break
				if verbose: log.write( "SND>"+str(l_count)+": \"" + l_block + "\"")
			#time.sleep(1)
			# Wait until all responses have been received.
			while l_count > g_count :
				try:
					out_temp = s.readline().strip() # Wait for grbl response
				except:
					if verbose : log.write("\nG-code block read error!")
					pass
				if out_temp.find('ok') < 0 and out_temp.find('error') < 0 :
					if verbose : log.write ( "    MSG: \""+out_temp+"\"") # Debug response
				else :
					if out_temp.find('error') >= 0 or out_temp == 0 : error_count += 1
					g_count += 1 # Iterate g-code counter
					if verbose : log.write("\nG-code file finished!")
					del c_line[0] # Delete the block character count corresponding to the last 'ok'
					if verbose: log.write( "  REC<"+str(g_count)+": \""+out_temp + "\""+str(sum(c_line)))
			# Wait for user input after streaming is completed
			if verbose : log.write("\nG-code streaming finished!"+ l_block);
			end_time = time.time();
			time.sleep(2);
			is_run = False;
			# try:
				# s.write("\r\n\r\n")
			# except:
				# if verbose : log.write("\n error s.write to gerbil")
				# pass
			#s.reset_input_buffer();
			if verbose : log.write ( " Time elapsed: "+str(end_time-start_time)+"\n");			
			if check_mode :
				if error_count > 0 :
					if verbose : log.write ( "CHECK FAILED:",str(error_count),"errors found! See output for details.\n")
				else :
					if verbose : log.write ( "CHECK PASSED: No errors found in g-code program.\n")
			else :
			   if verbose : log.write( "WARNING: Wait until Grbl completes buffered g-code blocks before exiting.")
			   time.sleep(2);
			try:
				s.reset_input_buffer()
				time.sleep(2);
			except:
				if verbose : log.write( "Error reset input port.")
				pass			
			try:
				# Close file and serial port
				#file_gcode.close()
				f.close()
			except:
				if verbose : log.write( "Error close file. "+ f)
				pass				
			try:
				s.close()
			except:
				if verbose : log.write( "Error close port.")
				pass
			try:
				log.close()
			except:
				if verbose : log.write( "Error close log.")
				pass
			#end_time = (time.time() - start_time)/60
			#inkex.errormsg(_("Completed in %mins... " %end_time ) )
		except:
			inkex.errormsg(_("No usb device found..."))

		#write parms used for this run to a text file DRG5
		parms = open(pos_file_parms, 'w')  #DRG5
		if self.options.bg_color == "#ffffff": #DRG5
			parms.write(" Replace transparency with " + "White") #DRG5
		else: #DRG5
			parms.write(" Replace transparency with " + "Black") #DRG5
		parms.write("\n Resolution = " + str(self.options.resolution)) #DRG5
		parms.write("\n Color to Greyscale conversion = " + str(self.options.grayscale_type)) #DRG5
		parms.write("\n B/W conversion algorithm = " + str(self.options.conversion_type)) #DRG5
		parms.write("\n B/W threshold (not gray scale option) = " + str(self.options.BW_threshold)) #DRG5
		parms.write("\n B/W max black value (nor gray scale option) = " + str(self.options.BWBlackvalue)) #DRG5
		parms.write("\n Grey Offset (gray scale option) = " + str(self.options.Grey_offset)) #DRG5
		parms.write("\n Compression/expansion (gray scale option) = " + str(self.options.Grey_multiplier)) #DRG5
		parms.write("\n Engraving speed " + str(self.options.speed_ON)) #DRG5
		if self.options.change30 == True: #DRG5
			parms.write("\n Modify $30 Value = " + "True") #DRG5
		else: #DRG5
			parms.write("\n Modify $30 Value = " + "False") #DRG5
		parms.write("\n $30 Value = " + str(self.options.PWM_Value)) #DRG5
		if self.options.flip_y == True: #DRG5
			parms.write("\n Flip Y-Axis = " + "True") #DRG5
		else: #DRG5
			parms.write("\n Flip Y-Axis = " + "False") #DRG5
		parms.write("\n Homing = " + str(self.options.homing)) #DRG5
		if self.options.offset == True: #DRG5
			parms.write("\n G0 XY Offsets from true home = " + "True") #DRG5
		else: #DRG5
			parms.write("\n G0 XY Offsets from true home = " + "False") #DRG5
		parms.write("\n G0 X-Offset from left home position in milimeters = " + self.options.xoffset) #DRG5
		parms.write("\n G0 Y-Offset from top home position in milimeters = " + self.options.yoffset) #DRG5
		parms.write("\n Whitespace acceleration = " + self.options.speedup) #DRG5
		parms.write("\n Minimum PWM = " + str(self.options.minPWM)) #DRG5
		parms.write("\n Laser ON Command = " + self.options.laseron) #DRG5
		parms.write("\n Laser OFF Command = " + self.options.laseroff) #DRG5
		parms.write("\n Select Gcode output option = " + str(self.options.streaming)) #DRG5
		parms.write("\n Workspace Coordinates = " + str(self.options.g54_value)) #DRG5
		parms.write("\n Run start time = " + run_start_time) #DRG5
		run_end_time = time.strftime('%X %x') #DRG5
		time_now = time.time() #DRG5
		parms.write("\n Run end time = " + run_end_time) #DRG5
		parms.write("\n Elapsed time = " + time.strftime('%H:%M:%S', time.gmtime(time_now - begin_time))) #DRG5
		parms.close() #DRG5
		return
	
	def serial_ports(self):
    # """ Lists serial port names

        # :raises EnvironmentError:
            # On unsupported or unknown platforms
        # :returns:
            # A list of the serial ports available on the system
    # """

		if sys.platform.startswith('win'):
			ports = ['COM%s' % (i + 1) for i in range(256)]
		elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
			# this excludes your current terminal "/dev/tty"
			ports = glob.glob('/dev/tty[A-Za-z]*')
		elif sys.platform.startswith('darwin'):
			ports = glob.glob('/dev/tty.*')
		else:
			raise EnvironmentError('Unsupported platform')

		result = []
		for port in ports:
			try:
				s = serial.Serial(port)
				s.close()
				result.append(port)
			except (OSError, serial.SerialException):
				pass
		return result
######## 	######## 	######## 	######## 	######## 	######## 	######## 	######## 	######## 	


def _main():
	e=GcodeExport()
	e.affect()
	
	
	exit()

if __name__=="__main__":
	_main()
