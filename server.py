from flask import Flask, request
import base64
from anpr import GetPlateNumber
import pymongo

mongoClient = pymongo.MongoClient("mongodb://localhost:27017/")
sdpDB = mongoClient["sdp"]
platesCol = sdpDB["plates"]
devicesCol = sdpDB["devices"]

app = Flask(__name__)

@app.route('/isVehicleAuthorized', methods=['POST'])
def isVehicleAuthorized():

    if 'image' not in request.json:
        return {"authorized": False, "msg": "The 'image' field is required"}

    if 'secret' not in request.json:
        return {"authorized": False, "msg": "The 'secret' field is required"}

    if devicesCol.find_one({"secret": request.json['secret']}) == None:
        return {"authorized": False, "msg": "Invalid secret"}
    
    with open('imgToTest.png', "wb") as fh:
        fh.write(base64.b64decode(request.json['image']))

    letter, num, _ = GetPlateNumber('imgToTest.png')
    print('\nDetected car letter:', letter)
    print('Detected car number:', num)

    p = platesCol.find_one({"number": num})
    if p == None:
        p = {"authorized": False, "letter": letter, "number": num}

    return {"authorized": p["authorized"], "letter": letter, "number": num}