#!/usr/bin/python
from PIL import Image
import sys

syntaxmessage = "Usage:    colorcode.py INPUTFILE [COLWIDTH=1] [ROWHEIGHT=1] [OUTPUTFILE=image.png]\nUsage:    colorcode.py -         [COLWIDTH=1] [ROWHEIGHT=1] [OUTPUTFILE=image.png]\nUse --single for an image consisting of a single row."

# complain if no input file
if len(sys.argv)<2:
	print syntaxmessage
	quit()

# print if ?; prompt for input if -; open file otherwise. message is filled after this block
message = ""
if sys.argv[1] == "?":
	print syntaxmessage
	quit()
elif sys.argv[1] == "-":
	message = raw_input("Enter input text: ")
else:
	try:
		f = open(sys.argv[1])
		message = f.read()
		message = message[:-1]
	except:
		print "File '"+sys.argv[1]+"' is not a valid input file."
		quit()

# If divisible by 3. If not, there are either 1 or 2 characters left over.
isTriplet = len(message)%3==0

# sizex (sizey) is the number of columns (rows)
# multx (multy) is the column width (row height) in pixels

# Single row
if "--single" in sys.argv:
	sizex = len(message)/3 + (not isTriplet)
	sizey = 1
	sys.argv.remove("--single")
# Attempt to square root; add one row, then one column, if not enough
else:
	sizex = int((len(message)/3+(not isTriplet))**(0.5))
	sizey = int((len(message)/3+(not isTriplet))**(0.5))
	if (sizex*sizey) < (len(message)/3+(not isTriplet)):
		sizey += 1
	if (sizex*sizey) < (len(message)/3+(not isTriplet)):
		sizex += 1
# sizex and sizey are now the correct value

# multx multy output, specified in that order; defaults to 1 1 image.png
multx = 1
multy = 1
output = "image.png"
if len(sys.argv)==2:
	pass
elif len(sys.argv)==3:
	try:
		multx = int(sys.argv[2])
		multy = multx
	except ValueError:
		print "Argument '"+sys.argv[2]+"' should be a number."
		quit()
elif len(sys.argv)==4:
	try:
		multx = int(sys.argv[2])
		multy =	int(sys.argv[3])
	except ValueError:
		print "Arguments '"+sys.argv[2]+"' and '"+sys.argv[3]+"' should be numbers."
		quit()
elif len(sys.argv)==5:
	try:
		multx = int(sys.argv[2])
		multy =	int(sys.argv[3])
	except ValueError:
		print "Arguments '"+sys.argv[2]+"' and '"+sys.argv[3]+"' should be numbers."
		quit()
	output = sys.argv[4]
else:
	print syntaxmessage
	quit()

# "colors small" -- array of unique colors
colorss = []
# step through the message in multiples of 3; do one more if not triplet
for i in range(len(message)/3 + (not isTriplet)):
	# no problem if triplet, just save (R,G,B) tuples
	if isTriplet:
		colorss.append((2*ord(message[i*3+0]),2*ord(message[i*3+1]),2*ord(message[i*3+2])))
	else:
		# be normal up till the last one
		if i<len(message)/3:
			colorss.append((2*ord(message[i*3+0]),2*ord(message[i*3+1]),2*ord(message[i*3+2])))
		else:
			# one character left over
			if len(message)%3==1:
				colorss.append((2*ord(message[i*3+0]),0,0))
			# two characters left over
			else:
				colorss.append((2*ord(message[i*3+0]),2*ord(message[i*3+1]),0))

# if sizex*sizey > number of colors (aka ceiling of len(message)), add white
while len(colorss)<=(sizex*sizey):
	colorss.append((255,255,255))

# "colors" -- true array of colors
colors = [(0,0,0)] * (sizex * sizey * multx * multy)
for i in range(sizex):
	for j in range(sizey):
		for x in range(multx):
			for y in range(multy):
				# i+j*sizex is the (i,j)th color in colorss;
				# i*multx + j*multy*sizex is the top left corner of the color box;
				# add x within box
				# add y*sizex*multx within box
				colors[(j*multy + y)*sizex*multx + (i*multx + x)] = colorss[i+j*sizex]

# write to file
im = Image.new("RGB",(sizex*multx,sizey*multy))
im.putdata(colors)
try:
	im.save(output)
except KeyError:
	print "'"+output+"' is not a valid output filename."
	quit()
print "'"+output+"'","created:",sizex*multx,"x",sizey*multy,"px,",sizex,"x",sizey,"colors."
