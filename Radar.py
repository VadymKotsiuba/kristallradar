import serial
import time
from threading import Timer
from tkinter import *
from PIL import *
from PIL import Image
from PIL import ImageTk
from PIL import ImageFont
from PIL import ImageDraw

#constants
digit_width = 18
screen_width = 64
y_shift = 1

serial_port = '/dev/ttyUSB0'
serial_speed = 9600

font_name = "/home/pi/scripts/radarfont.ttf"
font_size = 30

time_image_update = 2

myColor = 'black'
myX = 0
myY = 0

#variables
speedValue = 0
displayValue = 0
data = [0,0,0,0,0,0,0,0]
logNoData = False

def setColor(color):#string
    global myColor
    myColor = color

def setPosition(x_pos,y_pos):
    global myX
    global myY
    myX = x_pos
    myY = y_pos

def exitProgram(event):
    COMport.close()
    exit()

def checkSpeed():
    if 0<displayValue<=50:
        setColor('green')
    elif displayValue>50:
        setColor('red')
    else:
        setColor('black')
    if 0<=displayValue<10:
       setPosition((screen_width - digit_width)/2-2, y_shift)
    elif 10<=displayValue<100:
       setPosition((screen_width/2)-(42/2), y_shift)
    else:
       setPosition(0, y_shift)

def updateImage():
    global myImg
    toolDraw.rectangle([0,0,buffer.width-1,buffer.height-1], fill='black')
    toolDraw.text((myX,myY), str(displayValue), font=myFont, fill=myColor)
    pixels = buffer.load();
    for y in range(4):
        for x in range(64):
            pixels[x,y], pixels[x,y+4] = pixels[x,y+4], pixels[x,y]
            pixels[x,y+8], pixels[x,y+8+4] = pixels[x,y+8+4], pixels[x,y+8]
            pixels[x,y+16], pixels[x,y+16+4] = pixels[x,y+16+4], pixels[x,y+16]
            pixels[x,y+24], pixels[x,y+24+4] = pixels[x,y+24+4], pixels[x,y+24]
    myImg = ImageTk.PhotoImage(buffer)
    myLabel.config(image=myImg)
    myLabel.image = myImg

def readData():
    global data
    global speedValue
    global logNoData
    global zero_sec
    global displayValue

    if COMport.is_open:
        if COMport.in_waiting >= 8:
            data = COMport.read(8)
            if data[0+4] == 252 and data[1+4] == 250:
                if data[3+4] == 0:
                    speedValue = data[2+4]
                    logNoData = False
                else:
                    speedValue = 0
        else:
            if logNoData == False:
                    speedValue = 0
                    logNoData = True

    if speedValue < 10:
        if zero_sec >= 20:
            displayValue = 0
    else:
        zero_sec = 0
        displayValue = speedValue
    if speedValue > 199:
        displayValue = 199
    #comLabel.config(text = str(data[0])+' '+str(data[1])+' '+str(data[2])+' '+str(data[3]))

def timeUpdate():
    global sec
    global zero_sec
    time.sleep(0.1)
    sec += 1
    zero_sec += 1

#Init
COMport = serial.Serial(serial_port, serial_speed, timeout = None)
COMport.close()
COMport.open()
COMport.reset_input_buffer()

GUI = Tk()
GUI.title('Radar v0.1.2')
GUI.overrideredirect(True)
GUI.resizable(False, False)
GUI.geometry('64x32+500+400')
GUI.configure(bg='black')
GUI.bind('<Escape>', exitProgram)

myFont = ImageFont.truetype(font_name, font_size)

buffer = Image.new("RGB", (64,32), "black")
toolDraw = ImageDraw.Draw(buffer)
toolDraw.text((0,0), str(speedValue), font=myFont, fill='black')

myImg = ImageTk.PhotoImage(buffer)

myLabel = Label(GUI, image=myImg)
myLabel.image = myImg
myLabel.place(x = -1, y = -1)

updateImage()
sec = 0
zero_sec = 0

dataFile = open("/home/pi/scripts/started.txt", "r")
countStart = int(dataFile.readline())
dataFile.close()

countStart+=1

dataFile = open("/home/pi/scripts/started.txt", "w")
dataFile.write(str(countStart))
dataFile.close()

while 1:
    COMport.reset_input_buffer()
    timeUpdate()
    readData()
    checkSpeed()
    if sec >= 5:
        updateImage()
        sec = 0
    GUI.update_idletasks()
    GUI.update()

