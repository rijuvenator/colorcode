#!/usr/bin/python
from PIL import Image
import sys

# open image file, get data, get size
try:
	im = Image.open(sys.argv[1])
except:
	print "Invalid input file."
	quit()
data = list(im.getdata())
x, y = im.size

# the number of LSBs is the area times 3 for RGB
bits = [0] * (x*y*3)

# fill bits with the LSB from RGB, respectively
for i,tup in enumerate(data):
	bits[3*i + 0] = tup[0]%2
	bits[3*i + 1] = tup[1]%2
	bits[3*i + 2] = tup[2]%2

# the number of characters is the number of bytes;
# no need to ceiling because you can't store ASCII in less than 8 anyway
nums = [0] * (len(bits)/8)

# fill nums with int('8 bits at a time',2); convert to ASCII
message = ''
for i in range(len(bits)/8):
	nums[i] = int(''.join([str(x) for x in bits[i*8:i*8+8]]),2)
	message += chr(nums[i])

# strip the zeroes
print message.rstrip(chr(0))
