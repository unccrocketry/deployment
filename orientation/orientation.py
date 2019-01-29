'''
This code uses the micropython pyboard with an XBee.
The orientation() function can be called to use the pyboard's on-board accelerometer for leveling
'''
import pyb
import math
from pyb import UART
from machine import Pin
import time

#Peripheral(s) Initialization
uart = UART(3, baudrate=9600)       # create UART object
accel = pyb.Accel()                 # create object to access Pyboard's built-in accelerometer
orientServo = pyb.Servo(1)          # Create a servo object 'orientServo' as a pin1 connection\


#Constants Definitions
CW = -90                            # Value for Clockwise Servo Rotation
CCW = 90                            # Value for Counterclockwise Servo Rotation
Stop = -10                          # Value to Stop Servo Rotation
thresh_xacc = 22                    # Value of the x-axis accelerometer reading once airframe is considered to be in the proper orientation.

# Orientation Function. Accepts no arguments.
# Required Global Objects/Definitions: {uart, orientServo, accel, CW, CCW, Stop}
def orientation():                  
    completed=0
    uart.write('Stopping Servo')
    orientServo.speed(Stop)
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
                while accel.x()< thresh_xacc:
                    orientServo.speed(CCW)
                completed=1
                orientServo.speed(Stop)
            if state_y < 0:
                uart.write('CW')
                while accel.x()< thresh_xacc:
                    orientServo.speed(CW)
                completed=1
                orientServo.speed(Stop)
        elif state_x < 0:
            if state_y > 0:
                uart.write('CW')
                while accel.x()< thresh_xacc:
                    orientServo.speed(CW)
                completed=1
                orientServo.speed(Stop)
            if state_y < 0:
                uart.write('CCW')
                while accel.x()< thresh_xacc:
                    orientServo.speed(CCW)
                completed=1
                orientServo.speed(Stop)

orientation() #Call the function
