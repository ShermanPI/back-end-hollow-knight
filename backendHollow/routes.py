from backendHollow import app, mongo
from flask import Response, request, jsonify
from bson import json_util
from bson.objectid import ObjectId


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
                "id": str(id.inserted_id),
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
    characters = mongo.db.characters.find() #returns a BSON, and its a cursor
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
        "message": f'The character with ID {id} was succefully deleted'
    })
    return response


@app.route("/characters/<id>", methods = ["PUT"])
def updateUser(id):
    characterToUpdate = mongo.db.characters.find_one({"_id": ObjectId(id)})

    characterName = request.json.get('characterName', characterToUpdate["characterName"])
    characterImgSrc = request.json.get('characterImgSrc', characterToUpdate["characterImgSrc"])
    characterMainInfo = request.json.get('characterMainInfo', characterToUpdate["characterMainInfo"])
    characterSecondaryInfo = request.json.get('characterSecondaryInfo', characterToUpdate["characterSecondaryInfo"])

    mongo.db.characters.update_one({"_id": ObjectId(id)}, {"$set": {
        "characterName": characterName, 
        "characterImgSrc": characterImgSrc,
        "characterMainInfo": characterMainInfo,
        "characterSecondaryInfo": characterSecondaryInfo
        }})
    
    response = jsonify({
        'message': f'The characters with ID {id} has been updated successfully'
    })

    return response

@app.errorhandler(400)
def bad_request(error = None):
    response = jsonify({
        'message': "Bad Request: The request cannot be processed due to incorrect syntax or invalid data."
    })

    return response, 400
