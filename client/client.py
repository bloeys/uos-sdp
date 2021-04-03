import time
import sensor
import camera
import requests

def tick():
    
    dist = sensor.getDistanceCM()
    if dist > 2000:
        return

    print('close object ('+str(dist)+').' + 'Taking image and sending...')
    b64 = camera.getImageBase64()
    resp = requests.post("http://139.59.157.62:5000/isVehicleAuthorized", json={'secret':'5sa6riB1v2vgHL$2b!p5uPDUuUR9yxHZQ7pVUz0G', 'image': b64})
    if resp.status_code >= 400:
        try:
            print('unexpected error when calling the server. Resp: ', resp.text())
        finally:
            return

    j = resp.json()
    print('JJJ:',j)
    if j['authorized'] == False:
        print('Unauthorized')
        return

    time.sleep(20)
    while sensor.getDistanceCM() < 2000:
        time.sleep(0.5)

while True:
    tick()
    time.sleep(1)