from flask import Flask, request
import base64
from anpr import GetPlateNumber
import pymongo

mongoClient = pymongo.MongoClient("mongodb://localhost:27017/")
sdpDB = mongoClient["sdp"]
platesCol = sdpDB["plates"]

app = Flask(__name__)

@app.route('/isVehicleAuthorized', methods=['POST'])
def isVehicleAuthorized():

    with open('imgToTest.png', "wb") as fh:
        fh.write(base64.b64decode(request.json['image']))

    letter, num, _ = GetPlateNumber('imgToTest.png')
    print('\nDetected car letter:', letter)
    print('Detected car number:', num)

    p = platesCol.find_one({"number": num})
    if p == None:
        p = {"authorized": False, "letter": letter, "number": num}

    return {"authorized": p["authorized"], "letter": letter, "number": num}