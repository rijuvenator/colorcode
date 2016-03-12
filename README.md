# Color Code Script

This is a Python 2.7 script to encrypt ASCII text as an RGB color grid.

## Requirements
This script requires Python and Pillow, a Python image processing library. To install Pillow on OS X, first install pip:
````
sudo easy\_install pip
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
    * Specify neither (in which case every pixel will be assumed to be a new color; equivalent to `decode.py INPUTFILE 1 1`)
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
  * `i_am.txt` is a final published version of the same poem which differs slightly; it's interesting to compare the two images
  * `desiderata.txt` is the Desiderata by Max Ehrmann
