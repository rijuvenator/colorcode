import argparse
import math
from PIL import Image
import itertools

########################
#### PRETTY PRINTER ####
########################
def colorize(arg, color=None, end=True):
    colorCodes = {
        None   : '',
        'bold' : 1,
        'red'  : 31,
        'green': 32,
        'blue' : 34,
        'pink' : 35,
        'cyan' : 36,
    }
    CODE = colorCodes[color]
    return '\033[{}m{}{}'.format(CODE, arg, '' if not end else '\033[m')

def bold(arg):
    return colorize(arg, 'bold')

###############################
#### STEGANOGRAPHY ENCODER ####
###############################

class SteganographyCode():

    # constants
    NBITS = 8
    NCHAN = 3

    # initialize with parsed arguments
    # args should have INPUT, DECODE, and possibly MESSAGE
    def __init__(self, args):

        self.args = args
        
        # get the input image
        if args.INPUT is None:
            raise Exception('No image file specified')
        try:
            self.image = Image.open(args.INPUT)
            print('Opening {}'.format(bold(self.args.INPUT)))
        except:
            raise Exception('Error when trying to open image file {}'.format(bold(self.args.INPUT)))

        # get the input message
        if not args.DECODE:
            if args.MESSAGE == '-':
                self.message = input('{}: {}'.format(bold('Enter message here'), colorize('', 'blue', False)))
                print('\033[m', end='')
            else:
                try:
                    self.message = open(args.MESSAGE).read()
                    print('Reading text from {}'.format(bold(args.MESSAGE)))
                except:
                    raise Exception('Error reading from {}'.format(args.MESSAGE))

    # given a letter and a bit number n,
    # return the nth bit (from the left)
    # e.g. 'A', 1 --> 01000001 --> 1
    def getBit(letter, n):
        # 'A' --> 65
        AsciiCode = ord(letter)

        # 65 --> '0b1000001' --> '01000001'
        binStr = str(bin(AsciiCode))[2:].rjust(SteganographyCode.NBITS, '0')

        # int of nth bit
        return int(binStr[n])

    # do the encoding step
    def encode(self):

        # get the data and turn it into lists so that it can be modified
        data = [list(tup) for tup in list(self.image.getdata())]

        # initialize the message bits and make sure the message can fit
        bits = [0] * (SteganographyCode.NBITS * len(self.message))

        print('Image can hold {} characters, message has {}: '.format(
            bold(len(data)*SteganographyCode.NCHAN//8),
            bold(len(self.message))
        ), end='')
        if len(bits) > len(data)*SteganographyCode.NCHAN:
            print(colorize('Message too large', 'red'))
            raise Exception('Image is not big enough to hold the whole message')
        else:
            print(colorize('OK', 'green'))

        # fill in the bits
        # i indexes the letter, so skip forward by NBITS each letter
        # j indexes the bit, get the bit with the getBit function
        for i, letter in enumerate(self.message):
            for j in range(SteganographyCode.NBITS):
                bits[SteganographyCode.NBITS * i + j] = SteganographyCode.getBit(letter, j)

        # set all the LSBs in the actual image to 0
        # in a colorcode image, this step doesn't do anything
        # but in a normal image, this step ensures that junk
        # doesn't get decoded
        for i, triplet in enumerate(data):
            data[i] = [j-1 if j%2 == 1 else j for j in triplet]

        # group the bits into triplets to get a pixel number (with i//3)
        # which channel the bit is within the pixel is i%3 (0, 1, 2)
        # add 1 to the channel if the bit to be set is 1 (all LSBs are 0, before)
        for i, bit in enumerate(bits):
            pixelNumber = i//3
            channelNumber = i%3
            if bit:
                data[pixelNumber][channelNumber] += 1

        # image likes lists of tuples
        self.newData = [tuple(i) for i in data]

    # write to a new image file
    def write(self):
        if not hasattr(self, 'newData'):
            self.encode()

        image = Image.new('RGB', self.image.size)
        image.putdata(self.newData)

        OUTPUT = 'steg_'+self.args.INPUT

        image.save(OUTPUT)

        print('{} created'.format(bold(OUTPUT))) 
        print('Decode {} with : {}'.format(
            bold(OUTPUT),
            colorize('python steganography.py --inputimage {} --decode'.format(OUTPUT), 'pink')
        ))

    # if DECODE is true,
    # don't input a message or use it
    def decode(self):

        print('Attempting to decode {}:'.format(bold(self.args.INPUT)))
        print()

        data = list(self.image.getdata())
        bits = []

        # loop over every channel in every triplet
        # add 0 if % 2 is 0 otherwise 1
        for triplet in data:
            for channel in triplet:
                bits.append(0 if channel%2==0 else 1)

        # chunk the bits together in groups of 8
        # stringify each bit in the slice, join them, and add a 0b
        # interpret the string as an integer in base 2 and convert to character
        # strip 0s from the end
        message = ''
        for i in range(0, len(bits), SteganographyCode.NBITS):
            binStr = '0b' + ''.join([str(n) for n in bits[i:i+SteganographyCode.NBITS]])
            message += chr(int(binStr, 2))

        return message.strip(chr(0))


###############################
#### MAIN ARGPARSE AND RUN ####
###############################

parser = argparse.ArgumentParser(formatter_class=lambda prog: argparse.HelpFormatter(prog,max_help_position=45))
parser.add_argument('-i' , '--inputimage', dest='INPUT'  , default=None       ,                    help='input image'                      )
parser.add_argument('-m' , '--message'   , dest='MESSAGE', default='-'        ,                    help='input message'                    )
parser.add_argument('-d' , '--decode'    , dest='DECODE' , action='store_true',                    help='whether to decode an image file'  )
args = parser.parse_args()

coder = SteganographyCode(args)

if not args.DECODE:
    coder.write()

else:
    print(colorize(coder.decode(), 'blue'))
