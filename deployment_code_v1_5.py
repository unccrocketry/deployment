# main.py -- Deployment Code

from pyb import UART
import pyb
import math
from machine import Pin
import time
from pyb import Pin, Timer

#Peripheral initialization
uart = UART(3, baudrate=9600)
accel = pyb.Accel()   

#Servo Initialization
Sep_Servo = pyb.Servo(1)
Stabil_Servo = pyb.Servo(2)
orientServo = pyb.Servo(3)
Table_Servo = pyb.Servo(4)
p = Pin('X6')
tim = Timer(8, freq=50)
ArmDep_Servo = tim.channel(1, Timer.PWM, pin=p)


#Limit switch and LED initialization
Sep_SW = Pin('Y12', Pin.IN, Pin.PULL_UP)
Table_SW = Pin('Y11', Pin.IN, Pin.PULL_UP) 
R_led = pyb.LED(1)
G_led = pyb.LED(2)
O_led = pyb.LED(3)
B_led = pyb.LED(4)

#Constants Definition for Orientation
CW = 99
CCW = 99 #Make both directions the same value. We don't care to rotate in two directions. 
#CCW = -99 #Uncomment this to add a second direction for possible rotation.

Stop = 0

#Timers for the deployment process
Sep_Limit = 60+60+30		#2 min 30 seconds
Stabil_Limit = 12		#12 seconds
ArmDep_Limit = 1*5*.5		#This was arbitrarily chosen, need to update when completed


#Start message
uart.write('Welcome..')
uart.write('Setting servos to stop.')
uart.write('Type UNCC to begin deployment or numbers 1-5 for servo control.')
Sep_Servo.speed(Stop)
Stabil_Servo.speed(Stop)
orientServo.speed(Stop)
Table_Servo.speed(Stop)
ArmDep_Servo.pulse_width_percent(0)


#Determine threshold values based on pitch.
def determineThresh():
	z = accel.z()

	if z < -5 and z >= -7:
		return 20
	if z < -7 and z>= -11:
		return 20
	if z < -11 and z>= -15:
		return 18
	if z < -15:
		return 15

	if z <= 5 and z >= -5:
		return 22

	if z > 5 and z <= 7:
		return 20
	if z > 7 and z<= 11:
		return 18
	if z > 11 and z<= 15:
		return 15
	if z > 15:
		return 12

# Orientation Function. Accepts no arguments.
# Required Global Objects/Definitions: {uart, orientServo, accel, CW, CCW, Stop}
def orientation():
	completed=0                     #Validation bit to check if orientation is complete.
	thresh_xacc = determineThresh()
	uart.write('Threshold:')
	uart.write(thresh_xacc)
	uart.write('Setting servo speed(s) to 0') 
	orientServo.speed(Stop)

	while completed==0:
		uart.write('Starting Calibration')
		xacc= accel.x()
		yacc = accel.y()
		zacc = accel.z()

        # Obtain the polarities of each accelerometer axis reading (Mapping to unit circle quadrants)
		STATEX = 1
		STATEY = 1
		state_x = math.copysign(STATEX,xacc)    #Returns (-1/+1) for (-x/+x) accelerometer readings
		state_y = math.copysign(STATEY,yacc)    #Returns (-1/+1) for (-y/+y) accelerometer readings

        #Identifying which quadrant the acceleration vector falls on the unit circle and the required direction to bring platform to level.
		if state_x > 0:
			if state_y > 0:
				uart.write('CW')
				while accel.x()< thresh_xacc:   #Execute until x-acceleration has reached threshold va  lue
					orientServo.speed(CCW)      #Set direction of servo to CCW        
				completed=1                     #Make sure to break out of the while loop
				orientServo.speed(Stop)         #Stop spinning servo(s)
			if state_y < 0:
				uart.write('CCW')
				while accel.x()< thresh_xacc:   #Execute until x-acceleration has reached threshold value
					orientServo.speed(CW)
				completed=1                     #Make sure to break out of the while loop
				orientServo.speed(Stop)         
		elif state_x < 0:
			if state_y > 0:
				uart.write('CCW')
				while accel.x()< thresh_xacc:   #Execute until x-acceleration has reached threshold value
					orientServo.speed(CW)       
				completed=1                     #Make sure to break out of the while loop
				orientServo.speed(Stop)
			if state_y < 0:
				uart.write('CW')
				while accel.x()< thresh_xacc:   #Execute until x-acceleration has reached threshold value
					orientServo.speed(CCW)
				completed=1                     #Make sure to break out of the while loop
				orientServo.speed(Stop)
	uart.write('Orientation complete..')

def deployment():
	Sep_Count =0
	Stabil_Count =0
	ArmDep_Count =0
	Level_Check1 =0
	Level_Check2 =0
	Sep_Check =0 
	i = 0


	#**Initial Separation**
	uart.write('Initial Separation.\n')
	while Sep_Count < Sep_Limit:            	#Separate x inches to set up orientation. Should sep for 2 min and 30 ish seconds
		Sep_Servo.speed(CW)			#Turn counter clockwise to open (Matt Said)
		pyb.delay(1000)
		Sep_Count = Sep_Count + 1												
	Sep_Servo.speed(Stop)
	uart.write('Initial Separation Comlpete.\n')

	pyb.delay(3000)	

	#**Orientation 1**
	uart.write('Initial Orientation.\n')
	if Sep_Count >= Sep_Limit and Level_Check1 == 0:	
		orientation()
		Level_Check1 = 1
		O_led.on()					#Using this LED to how see how things are going
	uart.write('Orientation complete.\n')

	pyb.delay(3000)

	#**Separation**
	uart.write('Full Separation.\n')
	while Sep_SW.value() != 0 and Level_Check1 == 1:     	#Separate until limit switch is met
		Sep_Servo.speed(CW)				#Turn counter clockwise to open (Matt Said)
		Sep_Check = 1
	Sep_Servo.speed(Stop)
	uart.write('Full housing separation complete.\n')


	pyb.delay(3000)

	#**Stabilization**
	uart.write('Deploying stabilization legs./n')
	while Stabil_Count < Stabil_Limit and Level_Check1 == 1 and Sep_Check == 1:   #Open stabilization until count is met
		Stabil_Servo.speed(CCW)
		B_led.off()
		G_led.on()
		pyb.delay(1000)
		Stabil_Count = Stabil_Count+1
	Stabil_Servo.speed(Stop)
	uart.write('System stabilized.\n')	

	pyb.delay(3000)

	#**Orientation 2**
	uart.write('Reorienting../n')
	if Sep_Count >= Sep_Limit and Sep_SW.value() == 0 and Level_Check2 == 0 and Stabil_Count >= Stabil_Limit:
		orientation()					#Call orientation function here
		Level_Check2 = 1
		O_led.off()
		B_led.on()					#Using this LED to how see how things are going
	uart.write('System oriented./n')

	
	pyb.delay(3000)
	
	#**Table Lift**
	uart.write('Lifting the UAV table.. /n')
	while Stabil_Count >= Stabil_Limit and Table_SW.value() != 0 and Level_Check2 == 1:	#Lift Table until limit is met  		
		Table_Servo.speed(CCW)		
		G_led.off()
		R_led.on()
        	pyb.delay(1000)
	Table_Servo.speed(Stop)
	uart.write('UAV table is lifted. /n')		

	pyb.delay(3000)
		
	#** Drone Arm Deployment**
	uart.write('Deploying UAV arms. /n')
	while Table_SW.value() == 0 and ArmDep_Count < ArmDep_Limit: 
		ArmDep_Servo.pulse_width_percent(50) #Edit for counter clockwise
		R_led.off()
		G_led.on()
		pyb.delay(1000)
		DepSequence = True
	ArmDep_Servo.pulse_width_percent(0) 
	uart.write('UAV arms are deployed. /n')
	uart.write('UAV should be ready to deploy. /n')
	uart.write('Good luck /n')

def servoControl(serv):
	while True:
		pyb.delay(50)
		usrInput = str(uart.read())
		if 'a' in usrInput:
			serv.speed(10)
		if 'd' in usrInput:
			serv.speed(-10)
		if 's' in usrInput:
			serv.speed(0)
		if 'q' in usrInput:
			uart.write('Quitting..')
			serv.speed(0)
			break

def arm_servoControl(): #Tentative values
	while True:
		pyb.delay(50)
		usrInput = str(uart.read())
		if 'a' in usrInput:
			ArmDep_Servo.pulse_width_percent(5) 
		if 'd' in usrInput:
			ArmDep_Servo.pulse_width_percent(10) 
		if 's' in usrInput:
			ArmDep_Servo.pulse_width_percent(0) 
		if 'q' in usrInput:
			uart.write('Quitting..')
			ArmDep_Servo.pulse_width_percent(0) 
			break

while True:
	pyb.delay(250)
	daInput = str(uart.read())
	if 'UNCC' in daInput:
		deployment()
	if '1' in daInput:
		uart.write('Giving control over Sep servo..')
		servoControl(Sep_Servo)
	if '2' in daInput:
		uart.write('Giving control over Stabil servo..')
		servoControl(Stabil_Servo)
	if '3' in daInput:
		uart.write('Giving control over Orient servo..')
		servoControl(orientServo)
	if '4' in daInput:
		uart.write('Giving control over Table servo..')
		servoControl(Table_Servo)
	if '5' in daInput:
		uart.write('Giving control over Arm servo..')
		arm_servoControl()
	if 'OR' in daInput:
		uart.write('Performing Orientation test..')
		orientation()


