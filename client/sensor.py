import time
import RPi.GPIO as GPIO

GPIO_ECHO = 23
GPIO_TRIGGER = 24
ms = 1/1000
us = ms/1000

GPIO.setmode(GPIO.BCM)
GPIO.setup(GPIO_ECHO, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
 
def getDistanceCM():

    # Trigger sensor to start measuring distance
    GPIO.output(GPIO_TRIGGER, GPIO.HIGH)
    time.sleep(10 * us) 
    GPIO.output(GPIO_TRIGGER, GPIO.LOW)
 
    # Calculate time receiving a high signal
    GPIO.wait_for_edge(GPIO_ECHO, GPIO.RISING)
    startTime = time.time()
 
    GPIO.wait_for_edge(GPIO_ECHO, GPIO.FALLING)
    stopTime = time.time()

    highTime = stopTime - startTime
    return (highTime * 340) / 2 * 100
