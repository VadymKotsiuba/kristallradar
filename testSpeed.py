import time
from PIL import *
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
from rgbmatrix import RGBMatrix, RGBMatrixOptions

#constants
digit_width = 18
screen_width = 64;
y_shift = -8

font_name = "/home/pi/kristallradarlite/MachineBT.ttf"
#font_name = "/home/pi/scripts/radarfont.ttf"
font_size = 40

myColor = 'black'
myX = 0
myY = 0

#variables
logNoData = False
speedValue = 0

def setColor(color):#string
    global myColor
    myColor = color

def setPosition(x_pos,y_pos):
    global myX
    global myY
    myX = x_pos
    myY = y_pos

def checkSpeed():
    if 0<speedValue<=50:
        setColor('#00FF00')
       #setColor('#00af00')
    elif speedValue>50:
        setColor('#FF0000')
    else:
        setColor('#0000FF')
    if 0<=speedValue<10:
       setPosition((screen_width - digit_width)/2, y_shift)
    elif 10<=speedValue<100:
       setPosition((screen_width/2)-(42/2)+3, y_shift)
    else:
       setPosition(0+4, y_shift)

def updateImage():
    global toMatrixBuffer
    toolDraw.rectangle([0,0,buffer.width-1,buffer.height-1], fill='black')
    toolDraw.text((myX,myY), str(speedValue), font=myFont, fill=myColor)
    pixels = buffer.load();
    toMatrixPixels = toMatrixBuffer.load()
    for y in range(4):
        for x in range(64):
            pixels[x,y], pixels[x,y+4] = pixels[x,y+4], pixels[x,y]
            pixels[x,y+8], pixels[x,y+8+4] = pixels[x,y+8+4], pixels[x,y+8]
            pixels[x,y+16], pixels[x,y+16+4] = pixels[x,y+16+4], pixels[x,y+16]
            pixels[x,y+24], pixels[x,y+24+4] = pixels[x,y+24+4], pixels[x,y+24]
    for y in range(16):
        for x in range(64):
            toMatrixPixels[x,y] = pixels[x,y]
    for y in range(16,32):
        for x in range(64):
            toMatrixPixels[x+64,y-16] = pixels[x,y]      
    for y in range(16):
            for x in range(32):
                toMatrixPixels[x+32*0,y], toMatrixPixels[x+32*2,y] = toMatrixPixels[x+32*2,y], toMatrixPixels[x+32*0,y]
                toMatrixPixels[x+32*3,y], toMatrixPixels[x+32*1,y] = toMatrixPixels[x+32*1,y], toMatrixPixels[x+32*3,y]
    matrix.SetImage(toMatrixBuffer, 0, 0)

#myFont = ImageFont.truetype("Segment7Standard.otf", 36)
myFont = ImageFont.truetype(font_name,font_size)

buffer = Image.new("RGB", (64,32), "black")
toolDraw = ImageDraw.Draw(buffer)
toolDraw.text((0,0), str(speedValue), font=myFont, fill='black')

toMatrixBuffer = Image.new("RGB", (128,16), "black")


dataFile = open("/home/pi/kristallradarlite/started.txt", "r")
countStart = int(dataFile.readline())
dataFile.close()

countStart+=1

dataFile = open("/home/pi/kristallradarlite/started.txt", "w")
dataFile.write(str(countStart))
dataFile.close()

matrix_options = RGBMatrixOptions()
matrix_options.rows = 16
matrix_options.cols = 32
matrix_options.chain_length = 4
matrix_options.parallel = 1
matrix_options.multiplexing = 4
matrix_options.hardware_mapping = 'adafruit-hat'
matrix_options.gpio_slowdown = 2
matrix_options.pwm_bits = 1
#matrix_options.pwm_dither_bits = 1
matrix_options.brightness = 100
matrix_options.pwm_lsb_nanoseconds = 350
matrix = RGBMatrix(options = matrix_options)
matrix.SetImage(buffer, 0, 0)

while 1:
    for i in range(200):
        speedValue = i
        time.sleep(1)
        checkSpeed()
        updateImage()
