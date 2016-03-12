# Color Code Script

This is a Python 2.7 script to encrypt ASCII text as an RGB color grid.

## Requirements
This script requires Python and Pillow, a Python image processing library. To install Pillow on OS X, first install pip:
````
sudo easy_install pip
sudo -H pip install Pillow
````
If not already executable, make the scripts executable:
````
chmod +x colorcode.py decode.py
````

## Usage
### Encoding Text
To encode the text in a file, do
````
colorcode.py INPUTFILE [COLWIDTH] [ROWHEIGHT] [OUTPUTFILE]
````
To encode text from a command-line prompt, do
````
colorcode.py - [COLWIDTH] [ROWHEIGHT] [OUTPUTFILE]
````
Options:
  * Use `--single` for an image consisting of a single row; by default, a square-ish image will be produced
  * `COLWIDTH` is the column width in pixels; defaults to `1`
  * `ROWHEIGHT` is the row height in pixels; defaults to `COLWIDTH`
  * `OUTPUTFILE` is the name of the output image file; defaults to `image.png`

That is, `colorcode.py - 1 1 image.png` and `colorcode.py -` are equivalent.

The last two numbers from the output (the color dimensions) are important for decoding the image (see below)

### Decoding Text
To decode an image file produced in this way, do
````
decode.py INPUTFILE [COLS][ROWS]
````
Options:
  * `COLS` (`ROWS`) is the number of distinct columns (rows) in the image grid, or equivalently,  
    `COLS` (`ROWS) is the image width (height) divided by `COLWIDTH` (`ROWHEIGHT`)
    * Specify neither (then, every pixel will be assumed to be a new color; equivalent to `decode.py INPUTFILE 1 1`)
    * Specify both; just one number cannot be specified

The decoded text will be printed to the terminal.

## Example
`ring.txt` contains the Ring Inscription from The Lord of the Rings.  
`ring.png` was produced with
````
colorcode.py ring.txt 20 20 ring.png
````
producing the output
````
'ring.png' created: 220 x 240 px, 11 x 12 colors.
````
and can be decoded with
````
decode.py ring.png 11 12
````

I included additional poems as samples:
  * `ring.txt` is the Ring Inscription from The Lord of the Rings
  * `written_in_northampton_county_asylum.txt` is a poem by John Clare
  * `i_am.txt` is a final published version of the same poem differing slightly; comparing the images is interesting
  * `desiderata.txt` is the Desiderata by Max Ehrmann

## Details
### Overview
The script multiplies the ASCII value of each character by 2, and produces one color for every 3 characters, corresponding to the RGB value.

For example, "Dog" has ASCII values 68, 111, and 103, so the corresponding color would be RGB(136,222,206), or hex #88DECE.

### Why Multiply by 2?
The ASCII values were multiplied by 2 because ASCII characters end at 127, which means that direct RGB values of ASCII characters are rather dark, since they are restricted to the lower half of their spectrum. Conveniently, 126 is less than half of 255, so multiplying by 2 simply shifts the spectrum into the brighter half without overflow.

### Choosing Dimensions and the Number of Colors
A single row is an easy way to store the sequence of colors, suitable for short strings like names, but impractical for entire poems. An image that is close to square looks best, but the color dimensions also need to be integral. It's also slightly complicated by the fact that the required number of colors is the ceiling of the message length divided by 3.

So I took X = floor(L/3 + B), where L is the message length and B is 1 if L mod 3 = 0, 0 otherwise. That way, I add an extra color if L/3 is not divisible by 3, but keep the number of colors if it is. Then I set Y = X, and checked if XY < L/3 + B, added a row (Y = Y + 1) if not, checked if XY < L/3 + B again, and added a column (X = X + 1) if not. X and Y are then the final color dimensions.

I think this is the best way of getting as close to a square as possible without doing some weird Diophantine equation calculations, or trying to figure out which composite number area is closest to the message length divided by 3, and still guaranteeing I have enough squares to hold the entire message.

When L/3 mod 3 is not 0, the extra color has either R and G set, with B zero, or R set, with G and B zero. So the last color is usually darker than any of the others.

There are usually extra squares, because L/3 + B is usually not a square. The extra squares are filled with white.

When decoding the message, the 0 and 255 (divided by 2, of course) from the extra colors and extra squares are converted to ASCII too. Fortunately for me, 0 maps to NULL, and 127 maps to DEL, neither of which do anything when printed to a screen. Just in case you want to pipe the output to a file, though, to prevent the terminal from treating the text file like a binary file, I stripped all NULLs and DELs from the end of the decoded message. They were never part of the message anyway, and the result is the original input.
