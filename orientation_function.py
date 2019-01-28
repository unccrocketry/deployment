'''
This code uses the micropython pyboard with an XBee.
The orientation() function can be called to use the pyboard's on-board accelerometer for leveling
'''


import pyb
import math
from pyb import UART
from machine import Pin
import time

uart = UART(3, baudrate=9600)      # create UART object
CW = -90
CCW = 90
Stop = -10
daServo = pyb.Servo(1)
completed=0
accel = pyb.Accel()


def orientation():
    completed=0
    uart.write('Stopping Servo')
    daServo.speed(Stop)
    uart.write('Waiting for Signal')

    keySet = 0
    while keySet == 0:
         daInput = str(uart.read())
         if 'ok' in daInput:
            keySet = 1

    while completed==0:
        uart.write('Starting shit')
        uart.write('not yet completed')
        xacc= accel.x()
        yacc = accel.y()
        zacc = accel.z()
        uart.write(str(xacc))

        yf = float(yacc)
        xf = float(xacc)
        #ratio = yf/xf
        STATEX = 1
        state_x = math.copysign(STATEX,xacc)
        STATEY = 1
        state_y = math.copysign(STATEY,yacc)

        if state_x > 0:
            if state_y > 0:
                uart.write('CCW')
                while accel.x()< 22:
                    daServo.speed(CCW)
                completed=1
                daServo.speed(Stop)
            if state_y < 0:
                uart.write('CW')
                while accel.x()< 22:
                    daServo.speed(CW)
                completed=1
                daServo.speed(Stop)

        elif state_x < 0:
            if state_y > 0:
                uart.write('CW')
                while accel.x()< 22:
                    daServo.speed(CW)
                completed=1
                daServo.speed(Stop)
            if state_y < 0:
                uart.write('CCW')
                while accel.x()< 22:
                    daServo.speed(CCW)
                completed=1
                daServo.speed(Stop)

orientation()
