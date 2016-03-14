#!/usr/bin/python
from PIL import Image
import sys

# needs an image to work on
if len(sys.argv)<2:
	print "Specify an image."
	quit()

# open the image
try:
	im = Image.open(sys.argv[1])
except:
	print "'"+sys.argv[1]+"' is not a valid image file."
	quit()

# if a text file is specified, read it in; otherwise, prompt for input
if len(sys.argv)>=3:
	try:
		f = open(sys.argv[2])
		message = f.read()
		message = message[:-1]
	except:
		print "'"+sys.argv[1]+"' is not a valid input file."
		quit()
else:
	message = raw_input("Enter input text: ")

# get the image data
data = list(im.getdata())

# number of bits is 8 times the number of characters
bits = [0] * (8 * len(message))

# make sure the image can hold the whole message
x, y = im.size
if len(bits) > x*y*3:
	print "Image is not big enough to hold the whole message."
	quit()

# fill bits with each digit of the zero-padded binary representation of the ASCII value of each character
for i,letter in enumerate(message):
	for j in range(8):
		bits[8*i + j] = int("{0:0>8}".format(str(bin(ord(letter)))[2:])[j])

# set all 1's digit bits to zero; this is necessary to prevent junk if the message is shorter than the image
for i,tup in enumerate(data):
	tuplelist = list(tup)
	for j,num in enumerate(tuplelist):
		if num%2==1:
			tuplelist[j] = num - 1
	data[i] = tuple(tuplelist)

# the ith bit becomes the 1's digit of the i%3th value of the i/3th tuple
for i,bit in enumerate(bits):
	# python tuples are immutable
	tuplelist = list(data[i/3])

	# There were four cases when I did not originally set all bits to zero. Now there is only one case.
	# four cases:
	# bit = 1 and relevant bit is 1; do nothing
	#if bit and tuplelist[i%3]%2==1:
	#	pass
	# bit = 1 and relevant bit is 0; add 1 to relevant value
	#elif bit and tuplelist[i%3]%2==0:
	#	tuplelist[i%3] += 1
	# bit = 0 and relevant bit is 1; subtract 1 from relevant value
	#elif (not bit) and tuplelist[i%3]%2==1:
	#	tuplelist[i%3] -= 1
	# bit = 0 and relevant bit is 0; do nothing
	#elif (not bit) and tuplelist[i%3]%2==0:
	#	pass
	# then convert back to tuple

	if bit:
		tuplelist[i%3] += 1

	data[i/3] = tuple(tuplelist)

# save the image
im2 = Image.new("RGB",(x,y))
im2.putdata(data)
im2.save("encoded_"+sys.argv[1])
