import time
import base64
import picamera
from io import BytesIO
import io
camera = picamera.PiCamera()

# Settings
camera.led = True
camera.vflip = True
camera.hflip = True
# 3280×2464 for still photos, and 1920×1080
camera.resolution = (1920, 1080)
camera.zoom = (0.0, 0.0, 1.0, 1.0)
time.sleep(2)
# camera.start_preview()
# time.sleep(5)
# camera.stop_preview()

def getImageBase64():
    
    imgStream = BytesIO()
    camera.capture(imgStream, format='png')
    
    b64 = base64.b64encode(imgStream.getvalue())
    imgStream.close()
    #camera.capture('/home/pi/Desktop/dev/uos-sdp/client/capture.png', format='png')
    return b64
