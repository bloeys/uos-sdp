import time
import base64
import picamera
from io import BytesIO

camera = picamera.PiCamera()

# Settings
camera.led = True
camera.vflip = True
camera.hflip = True
# 3280×2464 for still photos, and 1920×1080
camera.resolution = (1920, 1080)
time.sleep(2)

def getImageBase64():
    
    imgStream = BytesIO()
    camera.capture(imgStream, format='png')
    
    b64 = base64.b64encode(imgStream.getvalue())
    imgStream.close()
    return b64
