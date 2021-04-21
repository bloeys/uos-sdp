import time
import RPi.GPIO as GPIO

GPIO_ECHO = 23
GPIO_TRIGGER = 24
GPIO_ECHO2 = 25
GPIO_TRIGGER2 = 8

ms = 1/1000
us = ms/1000

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(GPIO_ECHO, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(GPIO_ECHO2, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_TRIGGER2, GPIO.OUT)
 
def getDistanceCM(sideSensor = False):

    trigPin = GPIO_TRIGGER2 if sideSensor else GPIO_TRIGGER
    echoPin = GPIO_ECHO2 if sideSensor else GPIO_ECHO

    # Trigger sensor to start measuring distance
    GPIO.output(trigPin, GPIO.HIGH)
    time.sleep(10 * us) 
    GPIO.output(trigPin, GPIO.LOW)
 
    # Calculate time receiving a high signal
    
    #GPIO.wait_for_edge(echoPin, GPIO.RISING)
    readStart = time.time()
    startTime = time.time()
    while GPIO.input(echoPin) == GPIO.LOW:
        startTime = time.time()
        if time.time() - readStart > 3:
          return 1000
 
    #GPIO.wait_for_edge(echoPin, GPIO.FALLING)
    readStart = time.time()
    stopTime = time.time()
    while GPIO.input(echoPin) == GPIO.HIGH:
        stopTime = time.time()
        if time.time() - readStart > 3:
          return 1000

    pulseWidth = stopTime - startTime
    return (pulseWidth * 340) / 2 * 100
