import time
import base64
import picamera
from time import sleep
from io import BytesIO

camera = picamera.PiCamera()

# Settings
camera.led = True
camera.vflip = True
camera.hflip = True
# 3280×2464 for still photos, and 1920×1080
camera.resolution = (1920, 1080)
sleep(2)

imgStream = BytesIO()
camera.capture(imgStream, format='png')

imgStream.seek(0)
x = base64.b64encode(imgStream.read())
imgStream.close()
print(x)