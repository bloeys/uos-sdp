import time
import sensor
import camera
import requests
import RPi.GPIO as GPIO

GPIO_GREEN_LED=16
GPIO_RED_LED=21

#Mode and warnings are already set in the sensor package so no need here
#GPIO.setwarnings(False)
#GPIO.setmode(GPIO.BCM)

GPIO.setup(GPIO_GREEN_LED, GPIO.OUT)
GPIO.setup(GPIO_RED_LED, GPIO.OUT)

def ledOn(ledPin):
    GPIO.output(ledPin, GPIO.HIGH)

def ledOff(ledPin):
    GPIO.output(ledPin, GPIO.LOW)

def ledToggle(ledPin):
    newState = GPIO.LOW if GPIO.input(ledPin) == GPIO.HIGH else GPIO.HIGH
    GPIO.output(ledPin, newState)

def ledSet(ledPin, newState):
    GPIO.output(ledPin, newState)

def ledFlash(ledPin, flashCount, totalTime):
    startState = GPIO.input(ledPin)
    sleepDuration = totalTime/flashCount*0.5
    while flashCount > 0:
        ledToggle(ledPin)
        time.sleep(sleepDuration)
        ledToggle(ledPin)
        time.sleep(sleepDuration)
        flashCount -= 1

    ledSet(ledPin, startState)

def tick():
    
    ledOn(GPIO_GREEN_LED)
    ledOff(GPIO_RED_LED)

    dist = sensor.getDistanceCM()
    if dist > 200:
        return

    print('close object ('+str(dist)+').' + 'Taking image and sending...')
    b64 = camera.getImageBase64()
    try:
        resp = requests.post("http://139.59.157.62:5000/isVehicleAuthorized", json={'secret':'5sa6riB1v2vgHL$2b!p5uPDUuUR9yxHZQ7pVUz0G', 'image': b64}, timeout=10)
    except:
        ledOn(GPIO_RED_LED)
        ledOff(GPIO_GREEN_LED)
        time.sleep(3)
        return
            
    if resp.status_code != 200:
        try:
            print('unexpected response when calling the server. Resp: ', resp.text())
        finally:
            ledOn(GPIO_RED_LED)
            ledOff(GPIO_GREEN_LED)
            time.sleep(1)
            return

    respJSON = resp.json()
    print('server resp:', respJSON)
    if respJSON['authorized'] == False:
        print('Unauthorized car with number: ' + respJSON['number'])
        ledOff(GPIO_GREEN_LED)
        ledFlash(GPIO_RED_LED, 3, 3)
        return

    #Wait for car to start passing gate
    while sensor.getDistanceCM(sideSensor=True) > 200:
        ledFlash(GPIO_GREEN_LED, 2, 0.5)

    #Wait for car to completely pass gate
    while sensor.getDistanceCM(sideSensor=True) < 200:
        ledFlash(GPIO_GREEN_LED, 5, 0.5)

while True:

    #Test all components
    #ledFlash(GPIO_GREEN_LED, 5, 1)
    #ledFlash(GPIO_RED_LED, 5, 1)
    #print('old:', sensor.getDistanceCM())
    #time.sleep(1)
    #print('new:', sensor.getDistanceCM(True))
    #time.sleep(1)
    #continue
    tick()
    ledOff(GPIO_GREEN_LED)
    time.sleep(1)
