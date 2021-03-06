#Purpose: To detect if an object exists in front of the robot and if so 
#follow the object while maintaining a certain distance

import time
import Robot
import RPi.GPIO as GPIO
from Adafruit_AMG88xx import Adafruit_AMG88xx 
#Sensor intitialization
GPIO.setmode(GPIO.BCM)

#Thermal Sensor initialization
tempsens = Adafruit_AMG88xx()

#Right Ultrasound Sensor
TRIGR = 22
ECHOR = 23

GPIO.setup(TRIGR, GPIO.OUT)
GPIO.setup(ECHOR, GPIO.IN)
GPIO.output(TRIGR, False)
#Left Ultrasound  Sensor
TRIGL = 19
ECHOL = 20

GPIO.setup(TRIGL, GPIO.OUT)
GPIO.setup(ECHOL, GPIO.IN)
GPIO.output(TRIGL, False)
#Forward Ultrasound Sensor
TRIGF = 5
ECHOF = 6

#PIR Sensor
#PIR = 16
#GPIO.setup(PIR,GPIO.IN)

GPIO.setup(TRIGF, GPIO.OUT)
GPIO.setup(ECHOF, GPIO.IN)
GPIO.output(TRIGF, False)

print("Distance Measurement In Progress... ")

print("Waiting For Sensors To Settle")
time.sleep(2)

#Adjust motor offset so wheels turn at same speed
LEFT_TRIM = 0
RIGHT_TRIM = -1

#Create robot object to use functions from Robot class
robot = Robot.Robot(left_trim = LEFT_TRIM, right_trim = RIGHT_TRIM, left_id = 1, right_id = 3)

#Calculate distance to object in front of the sensor           
def distance(trigger, echo):
   #Emit 10 usec pulse
    GPIO.output(trigger, True)
    time.sleep(0.00001)
    GPIO.output(trigger, False)

    pulse_start = time.time()
    pulse_end = time.time()
    #Record time for return echo
    while GPIO.input(echo) == 0:
        pulse_start = time.time()       
    while GPIO.input(echo) == 1:
        pulse_end = time.time()

    pulse_duration = pulse_end - pulse_start
    dist = pulse_duration * 17150
    dist = round(dist,2)
    #print(distance)
    return dist

# Returns the average temperature of objects found in the center of the IR camera's viewing range
def getTemp():
    tempa = tempsens.readPixels()
    average = (tempa[28]+tempa[29]+tempa[36]+tempa[37]+tempa[44]+tempa[45])/6
    print("Average temp is: %.2f " % average)
    return average


#Continuously maintain a constant distance from object until user quits program     
def followrl(distf, distr, distl):
    y = 1
    while True:
        if distf > 20 and distr > 50 and distl > 50 and getTemp() > 28 :
            robot.forward(150)
            print("FORWARD")
        elif distr < 50 and distr > 4 and distf > 10:
            robot.right(125)
            print("RIGHT")
        elif distl < 50 and distl > 4 and distf > 10:
            robot.left(125)
            print("LEFT")
        else:
            robot.stop()
            print("STOP")
        distf, distr, distl = 0, 0, 0
        for x in range(y):
            distf = (distf + distance(TRIGF, ECHOF))/y
            distr = (distr + distance(TRIGR, ECHOR))/y
            distl = (distl + distance(TRIGL, ECHOL))/y
        print("FORWARD DISTANCE:  %.1f cm \t RIGHT DISTANCE: %.1f cm \t LEFT DISTANCE: %.1f cm" % (distf, distr, distl))       
        distf = (distf + distance(TRIGF, ECHOF))
        distr = (distr + distance(TRIGR, ECHOR))
        distl = (distl + distance(TRIGL, ECHOL))
        



#Begin using robot by standing at a distance less than 20 cm. Robot will follow until program is escaped
if __name__ == '__main__':
    try:
        print("Measuring")
        dist = distance(TRIGF, ECHOF)
        distr = distance(TRIGR, ECHOR)
        distl = distance(TRIGL, ECHOL)
       #Measure distance but do not move until initialized
        human = getTemp()
        
        while dist > 20 and human < 28:
            dist = distance(TRIGF, ECHOF)
            distr = distance(TRIGR, ECHOR)   
            distl = distance(TRIGL, ECHOL)
            print("FORWARD DISTANCE:  %.1f cm \t RIGHT DISTANCE: %.1f cm \t LEFT DISTANCE: %.1f cm" % (dist, distr, distl))
            human = getTemp()
            time.sleep(1)

           
        followrl(dist, distr, distl)
                
    finally:
        print("Measurement stopped by User")
        robot.stop()
        GPIO.cleanup()
            
    



