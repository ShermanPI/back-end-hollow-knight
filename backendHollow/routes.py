from backendHollow import app
from flask_pymongo import PyMongo
from flask import Response, request, jsonify
from bson import json_util
from bson.objectid import ObjectId

app.config['MONGO_URI'] = "mongodb://127.0.0.1:27017/hollowDB"
mongo = PyMongo(app)

@app.route("/characters", methods=['POST'])
def addCharacter():
    payload = request.json

    characterImgSrc = payload.get('characterImgSrc', "")
    characterName = payload.get('characterName', "")
    characterMainInfo = payload.get('characterMainInfo', "")
    characterSecondaryInfo = payload.get('characterSecondaryInfo', "")

    if characterImgSrc and characterName and characterMainInfo:
        id = mongo.db.characters.insert_one(
            {"characterImgSrc": characterImgSrc, "characterName": characterName, "characterMainInfo": characterMainInfo, "characterSecondaryInfo": characterSecondaryInfo}
        )
        
        response = {
            "message": "Character created succesfully",
            "status": "success",
            "data": {
                "id": str(id),
                "characterName": characterName,
                "characterImgSrc": characterImgSrc,
                "characterMainInfo": characterMainInfo,
                "characterSecondaryInfo": characterSecondaryInfo
            }
        } 

        return response
    else:
        return bad_request()

@app.route("/characters", methods = ['GET'])
def getCharacters():
    characters = mongo.db.characters.find() #returns a BSON
    response = json_util.dumps(characters)

    return Response(response, mimetype="application/json")

@app.route("/characters/<id>", methods = ['GET'])
def getCharacter(id):
    character_in_bson = mongo.db.characters.find_one({"_id": ObjectId(id)})
    character_in_bson_to_string = json_util.dumps(character_in_bson)

    return Response(character_in_bson_to_string, mimetype="application/json")

@app.route("/characters/<id>", methods = ["DELETE"])
def deleteCharacter(id):
    mongo.db.characters.delete_one({"_id": ObjectId(id)})
    
    response = jsonify({
        "message": "The character with ID id was succefully deleted"
    })
    return response


@app.errorhandler(400)
def bad_request(error = None):
    response = jsonify({
        'status_code': 400,
        "status": "Bad Request",
        'message': "The request cannot be processed due to incorrect syntax or invalid data."
    })

    return response, 400
