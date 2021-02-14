from flask import Flask, request
import base64
from anpr import GetPlateNumber

app = Flask(__name__)

@app.route('/isVehicleAuthorized', methods=['POST'])
def isVehicleAuthorized():

    with open('imgToTest.png', "wb") as fh:
        fh.write(base64.b64decode(request.json['image']))

    letter, num, _ = GetPlateNumber('imgToTest.png')
    print('\nDetected car letter:', letter)
    print('Detected car number:', num)
    
    return {"authorized": True, "letter": letter, "number": num}