#!/usr/bin/python
from PIL import Image
import sys

syntaxmessage = "Usage:    decode.py INPUTFILE [COLS=width][ROWS=height]"

# complain if no input file
if len(sys.argv)<2:
	print syntaxmessage
	quit()

# print if ?; open file otherwise. data is filled after this block
if sys.argv[1]=="?":
	print syntaxmessage
	quit()
try:
	im = Image.open(sys.argv[1])
except IOError:
	print "File '"+sys.argv[1]+"' is not a valid image file."
	quit()
data = list(im.getdata())

# if sizex sizey specified, use them; otherwise, assume 1 pixel = 1 color
x, y = im.size
sizex = x
sizey = y
if len(sys.argv)==2:
	pass
elif len(sys.argv)==4:
	try:
		sizex = int(sys.argv[2])
		sizey = int(sys.argv[3])
	except ValueError:
		print "Arguments '"+sys.argv[2]+"' and '"+sys.argv[3]+"' should be numbers."
		quit()
else:
	print syntaxmessage
	quit()

# column width and row height can be gotten from x y sizex sizey
multx = x/sizex
multy = y/sizey

# loop through unique colors (not pixels); use the top right pixel.
# should be no problem if nothing has happened to the image file!
message = ""
for j in range(sizey):
	for i in range(sizex):
		message += chr(data[j*multy*sizex*multx + i*multx][0]/2)+chr(data[j*multy*sizex*multx + i*multx][1]/2)+chr(data[j*multy*sizex*multx + i*multx][2]/2)

# strip 0 and 127, the padder colors for non-multiples of 3 and non-squares
# then print
print message.rstrip(chr(127)+chr(0)+"\n")
