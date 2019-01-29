# main.py -- Deployment Code
# 1=red, 2=green, 3=yellow, 4=blue
from pyb import UART
import pyb
from machine import Pin
import time
from pyb import Pin, Timer


uart = UART(3, baudrate=9600)      # create UART object

Sep_Servo = pyb.Servo(1)
Stabil_Servo = pyb.Servo(2)
Orient_Servo = pyb.Servo(3)
Table_Servo = pyb.Servo(4)

#p = Pin('X6')
#tim = Timer(8, freq=50)
#ArmDep_Servo = tim.channel(1, Timer.PWM, pin=p)

Sep_SW = Pin('Y12', Pin.IN, Pin.PULL_UP)
Table_SW = Pin('Y11', Pin.IN, Pin.PULL_UP)
R_led = pyb.LED(1)
G_led = pyb.LED(2)
O_led = pyb.LED(3)
B_led = pyb.LED(4)

CW = -90
CCW = 90
Stop = -5
Sep_Limit = 5
Sep_Count = 0
Stabil_Limit = 5
Stabil_Count = 0
Level_Check1 = 0
Level_Check2 = 0
Sep_Check = 0
i = 0

while True:

    Sep_Servo.speed(Stop)
    #Stabil_Servo.speed(Stop)
    #Orient_Servo.speed(Stop)
    #Table_Servo.speed(Stop)
    #ArmDep_Servo.speed(Stop)


    #**Initial Separation**
    if Sep_Count < Sep_Limit:                                                        #Separate x inches to set up orientation
        Sep_Servo.speed(CW)
        pyb.delay(1000)
        Sep_Count = Sep_Count + 1

    #**Orientation 1**
    if Sep_Count >= Sep_Limit and Level_Check1 == 0:                                #Orientation 1: Insert Orientation Code in the logic
        Sep_Servo.speed(Stop)
        Level_Check1 = 1
        O_led.on()
        pyb.delay(1000)

    #**Separation**
    while Sep_Count >= Sep_Limit and Sep_SW.value() != 0 and Level_Check1 == 1:     #Separate until limit switch is met
        Sep_Servo.speed(CCW)
        Sep_Check = 1
        Orient_Servo.speed(Stop)

    #**Orientation 2**
    if Sep_Count >= Sep_Limit and Level_Check1 == 1 and Sep_SW.value() == 0 and Level_Check2 != 0:    #Orientation 2: Insert Orientation Code in the logic
        Sep_Servo.speed(Stop)
        Level_Check2 = 1
        O_led.off()
        B_led.on()
        pyb.delay(1000)

    #**Stabilization**
    while Stabil_Count < Stabil_Limit and Level_Check1 == 1 and Sep_SW.value() == 0 and Sep_Check == 1:                         #Open stabilization until count is met
        Sep_Servo.speed(CW)
        Orient_Servo.speed(Stop)
        B_led.off()
        G_led.on()
        pyb.delay(1000)

    #**Table Lift**
    while Stabil_Count >= Stabil_Limit and Table_SW.value() != 0 and Level_Check2 == 1:    #Lift Table until limit is met
        Sep_Servo.speed(CW)                #Change to "Table_Servo.speed(CW)
        #Stabil_Servo.speed(Stop)
        #Orient_Servo.speed(Stop)
        #Table_Servo.speed(Stop)
        #ArmDep_Servo.speed(Stop)
        G_led.off()
        R_led.on()
        pyb.delay(1000)
