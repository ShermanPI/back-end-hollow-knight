import secrets
import os
from flask import make_response, request, jsonify, session, url_for
from backendHollow import app, mongo
from backendHollow.forms import createCharacterForm
from bson import json_util
from bson.objectid import ObjectId



def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    f_name, f_extention = os.path.splitext(form_picture.filename)
    picture_filename = random_hex + f_extention
    picture_path = os.path.join(app.root_path, 'static/characters-images', picture_filename)
    form_picture.save(picture_path)
    return picture_filename


@app.route("/characters", methods = ["POST"])
def addCharacter():
    print("This is the object with the image", request.files)
    form = createCharacterForm(request.form)
    print(form.csrf_token.data, " SHAKJSDBN ", session["form_csrf_token"])
    if(form.csrf_token.data == session.get("form_csrf_token")):
        if(form.validate_on_submit()):
            picture_file = save_picture(request.files['characterImgSrc'])

            newCharacter = mongo.db.characters.insert_one({'characterName': form.characterName.data, 'characterMainInfo': form.characterMainInfo.data, 'characterSecondaryInfo': form.characterSecondaryInfo.data, 'characterImgSrc': picture_file})
            character = mongo.db.characters.find_one({'id': ObjectId(newCharacter.inserted_id)})
            return jsonify({
                'message': f"The character {form.characterName.data} has been added",
                'character': json_util.dumps(character)
                })
        else:
            response = make_response(jsonify({'errors': form.errors}))
            response.status_code = 409

            return response
    else:
        return forbidden()

@app.route("/characters", methods = ['GET'])
def getCharacters():
    characters = mongo.db.characters.aggregate([{"$project": {"characterImgSrc": {"$concat": [url_for('static', filename='characters-images/'), "$characterImgSrc"]}, "_id": 1, "characterName": 1, "characterMainInfo": 1, "characterSecondaryInfo": 1}}])
    response = json_util.dumps(characters)

    return make_response(response)

# @app.route("/characters", methods=['POST'])
# def addCharacter():
#     payload = request.json

#     characterImgSrc = payload.get('imgSrc', "")
#     characterName = payload.get('name', "")
#     characterMainInfo = payload.get('mainInfo', "")
#     characterSecondaryInfo = payload.get('secondaryInfo', "")

#     if characterImgSrc and characterName and characterMainInfo:
#         id = mongo.db.characters.insert_one(
#             {"imgSrc": characterImgSrc, "name": characterName, "mainInfo": characterMainInfo, "secondaryInfo": characterSecondaryInfo}
#         )
        
#         response = {
#             "message": "Character created succesfully",
#             "status": "success",
#             "data": {
#                 "id": str(id.inserted_id),
#                 "name": characterName,
#                 "imgSrc": characterImgSrc,
#                 "mainInfo": characterMainInfo,
#                 "secondaryInfo": characterSecondaryInfo
#             }
#         } 

#         return jsonify(response)
#     else:
#         return bad_request()

@app.route("/characters/<id>", methods = ['GET'])
def getCharacter(id):
    character_in_bson = mongo.db.characters.find_one({"_id": ObjectId(id)})
    character_in_bson_to_string = json_util.dumps(character_in_bson)

    return make_response(character_in_bson_to_string, mimetype="application/json")

@app.route("/characters/<id>", methods = ["DELETE"])
def deleteCharacter(id):
    mongo.db.characters.delete_one({"_id": ObjectId(id)})
    
    response = jsonify({
        "message": f'The character with ID {id} was succefully deleted'
    })
    return response


@app.route("/characters/<id>", methods = ["PUT"])
def updateCharacter(id):
    characterToUpdate = mongo.db.characters.find_one({"_id": ObjectId(id)})

    characterName = request.json.get('name', characterToUpdate["characterName"])
    characterImgSrc = request.json.get('imgSrc', characterToUpdate["characterImgSrc"])
    characterMainInfo = request.json.get('mainInfo', characterToUpdate["characterMainInfo"])
    characterSecondaryInfo = request.json.get('secondaryInfo', characterToUpdate["characterSecondaryInfo"])

    mongo.db.characters.update_one({"_id": ObjectId(id)}, {"$set": {
        "name": characterName, 
        "imgSrc": characterImgSrc,
        "mainInfo": characterMainInfo,
        "secondaryInfo": characterSecondaryInfo
        }})
    
    response = jsonify({
        'message': f'The character with ID {id} has been updated successfully'
    })

    return response

@app.errorhandler(403)
def forbidden(error = None):
    response = make_response(jsonify({"message": "The csrf_token were not validated"}))
    response.status_code = 403
    return response

@app.errorhandler(400)
def bad_request(error = None):
    response = jsonify({
        'message': "Bad Request: The request cannot be processed due to incorrect syntax or invalid data."
    })

    return response, 400