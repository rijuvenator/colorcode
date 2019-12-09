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

#########################
#### COLORCODE CLASS ####
#########################

class ColorCode():
    # constants
    WHITE  = (255, 255, 255)
    NULL   = chr(0)
    RGBLEN = 3

    # encapsulate the conversion from a character to a channel
    # in this case, it is simple: 2 * the ascii value of the character
    # static function (doesn't take self)
    def charToChannel(char):
        return 2 * ord(char)

    # initialize with parsed arguments
    # args should have INPUT, BLOCK, NCOLS, NROWS, OUTPUT
    def __init__(self, args):
        self.args = args

        # message: read from input or from a file
        if args.INPUT == '-':
            self.message = input('{}: {}'.format(bold('Enter message here'), colorize('', 'blue', False)))
            print('\033[m', end='')
        else:
            try:
                self.message = open(args.INPUT).read()
                print('Reading text from {}'.format(bold(args.INPUT)))
            except:
                raise Exception('Error reading from {}'.format(args.INPUT))

        # number of characters in the message
        self.nChars  = len(self.message)

        # number of blocks needed to encode the message
        # characters are grouped into 3s with one or two empties
        self.nBlocks = math.ceil(self.nChars / ColorCode.RGBLEN)

        # set dimensions
        self.sizeX, self.sizeY = self.computeDimensions()

        # get block size
        self.blockX, self.blockY = args.BLOCK

    # compute dimensions
    # with no constraints, make the dimensions square
    # otherwise, prioritize NCOLS over NROWS
    def computeDimensions(self):

        # neither NCOLS nor NROWS was specified
        # so define dimensions to be as square as possible
        if self.args.NROWS is None and self.args.NCOLS is None:
            sizeX, sizeY = self.getAutoDimensions()

        # NCOLS was specified
        elif args.NCOLS is not None:
            sizeX = args.NCOLS
            sizeY = math.ceil(self.nBlocks / sizeX)

        # NROWS was specified and NCOLS was not
        else:
            sizeY = args.NROWS
            sizeX = math.ceil(self.nBlocks / sizeY)

        return sizeX, sizeY

    # small method for getting approximately square dimensions
    # do this by rounding down the sqrt of the number of blocks
    # if the resulting square doesn't have enough blocks, add a row
    # if the resulting square+1 row doesn't have enough blocks, add a column
    # it cannot possibly need to be any bigger
    def getAutoDimensions(self):

        # square root it to get a candidate "square" dimension and round down
        sqrt = int( math.sqrt(self.nBlocks) )

        sizeX, sizeY = sqrt, sqrt

        # if this isn't the right size, add a row
        if sizeX * sizeY < self.nBlocks:
            sizeY += 1

        # if this isn't the right size, add a column
        if sizeX * sizeY < self.nBlocks:
            sizeX += 1

        # done now
        return sizeX, sizeY

    # compute the array of colors
    # i.e. the image as if it were 1x1 block size
    # instead of a more pythonic grouper, just slice through 3 at a time
    # for the very last block, it's possible that the slice is 1 or 2 characters
    # so tack on NULL characters until it's 3 characters
    # then, it's possible that nBlocks < sizeX * sizeY
    # so tack on WHITE squares until they're all filled up
    def fillColors(self):
        self.array = []
        for idx in range(0, self.nChars, ColorCode.RGBLEN):
            messageSlice = self.message[idx:idx+ColorCode.RGBLEN]
            while len(messageSlice) < ColorCode.RGBLEN:
                messageSlice += ColorCode.NULL
            self.array.append( tuple([ColorCode.charToChannel(char) for char in messageSlice]) )

        while len(self.array) < self.sizeX*self.sizeY:
            self.array.append(ColorCode.WHITE)

    # the actual image is the array, blown up by the block size
    # Image requires a 1D array with a tuple defining the size
    # pre-fill with a bunch of black squares
    # now i, j tells you which array cell you're considering: i + j*sizeX converts 2D (i, j) to 1D
    # and x, y tells you where within the block you are (they are all the same, of course)
    # blowing it up means i --> i*blockX + x, j --> j*blockY + y, sizeX --> sizeX*blockX
    def fillImage(self):
        if not hasattr(self, 'array'):
            self.fillColors()
        self.image = [(0, 0, 0)] * (self.sizeX * self.sizeY * self.blockX * self.blockY)

        for i, j, x, y in itertools.product(range(self.sizeX), range(self.sizeY), range(self.blockX), range(self.blockY)):
            self.image[(i*self.blockX + x) + (j*self.blockY + y)*self.sizeX*self.blockX] = self.array[i+j*self.sizeX]

    # write to file
    def write(self):
        if not hasattr(self, 'image'):
            self.fillImage()

        imFile = Image.new('RGB', (self.sizeX*self.blockX, self.sizeY*self.blockY))
        imFile.putdata(self.image)
        try:
            imFile.save(self.args.OUTPUT)
        except:
            raise Exception('Error when trying to write to {}'.format(bold(self.args.OUTPUT)))

        print('{} created: {} x {} px, {} x {} colors'.format(
            bold(self.args.OUTPUT),
            self.sizeX*self.blockX,
            self.sizeY*self.blockY,
            self.sizeX,
            self.sizeY,
        ))
        print('Decode {} with : {}'.format(
            bold(self.args.OUTPUT),
            colorize('python colorcode.py --decode --inputfile {} --ncols {} --nrows {}'.format(
                self.args.OUTPUT,
                self.sizeX,
                self.sizeY
            ), 'pink')
        ))

#######################
#### DECODER CLASS ####
#######################

class Decode():

    # load the args
    # open the image
    # get the height and width
    # if either or both of NCOLS and NROWS are not specified, assume block size is 1 x 1
    # otherwise, sizeX and sizeY are given, compute blockX and blockY from that and the image size
    def __init__(self, args):

        self.args = args

        try:
            self.image = Image.open(args.INPUT)
        except:
            raise Exception('Error when trying to open image file {}'.format(bold(self.args.INPUT)))

        self.width, self.height = self.image.size

        if self.args.NCOLS is None or self.args.NROWS is None:
            print('Color dimensions not specified; assuming block size = '+bold('1 x 1 px'))
            self.sizeX , self.sizeY  = self.width, self.height
            self.blockX, self.blockY = 1, 1

        else:
            self.sizeX , self.sizeY  = self.args.NCOLS           , self.args.NROWS
            self.blockX, self.blockY = int(self.width/self.sizeX), int(self.height/self.sizeY)

    # encapsulate the conversion from a channel to a character
    # in this case, it is simple: channel // 2 --> ascii
    # static function (doesn't take self)
    def channelToChar(code):
        return chr(code//2)

    # start with empty
    # get the list of color data
    # for each j (row), for each i (column),
    # the top right of the block is the usual formula for i --> image and j --> image (with x, y = 0)
    # as long as the image isn't corrupted, the top right is guaranteed to exist and is the same as the rest
    # each element is a list of three numbers, so get the characters and string them together
    # finally, strip off the NULLs, white boxes, and a final newline
    def getMessage(self):
        print('Attempting to decode {}:\n'.format(bold(self.args.INPUT)))
        message = ''
        data = list(self.image.getdata())
        for j, i in itertools.product(range(self.sizeY), range(self.sizeX)):
            topRight = (i)*self.blockX + (j*self.blockY)*self.blockX*self.sizeX
            message += ''.join([Decode.channelToChar(code) for code in data[topRight]])

        return message.rstrip(chr(127)+chr(0)+"\n")


###############################
#### MAIN ARGPARSE AND RUN ####
###############################

# in ordinary encode mode
# - provide an input TEXT file or - for stdin
# - provide an output file or accept that default of image.png
# - provide either ncols or nrows or neither; neither --> squareish, ncols takes precedence over nrows
# - provide a block size, i.e. the size of a block, width and height, e.g. 20 x 20 px blocks

# in decode mode
# - specify --decode
# - provide an input IMAGE file
# - provide BOTH ncols and nrows, informing the program how many blocks there are, or neither, assuming they're 1 x 1
# - can use the output line from the previous step

parser = argparse.ArgumentParser(formatter_class=lambda prog: argparse.HelpFormatter(prog,max_help_position=45))
parser.add_argument('-i' , '--inputfile' , dest='INPUT' , default='-'        ,                    help='input filename or - for raw input')
parser.add_argument('-o' , '--outputfile', dest='OUTPUT', default='image.png',                    help='output filename'                  )
parser.add_argument('-nr', '--nrows'     , dest='NROWS' , default=None       ,          type=int, help='number of rows'                   )
parser.add_argument('-nc', '--ncols'     , dest='NCOLS' , default=None       ,          type=int, help='number of columns'                )
parser.add_argument('-b' , '--blocksize' , dest='BLOCK' , default=[1, 1]     , nargs=2, type=int, help='block size X Y to scale up'       )
parser.add_argument('-d' , '--decode'    , dest='DECODE', action='store_true',                    help='whether to decode an image file'  )
args = parser.parse_args()

if not args.DECODE:
    image = ColorCode(args)
    image.write()

else:
    decoder = Decode(args)
    print(colorize(decoder.getMessage(), 'blue'))
