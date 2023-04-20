import secrets
import os
import json
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
    form = createCharacterForm(request.form)
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

@app.route("/charactersSample/<int:sample_size>", methods = ['GET', 'POST'])
def getCharactersSample(sample_size):
    if request.method == 'POST':
        already_rendered = request.json['items']
        characters = mongo.db.characters.aggregate([{"$match": {"characterName": {"$nin": already_rendered}}}, {"$sample": {"size": sample_size}}, {"$project": {"characterImgSrc": {"$concat": [url_for('static', filename='characters-images/'), "$characterImgSrc"]}, "_id": 1, "characterName": 1, "characterMainInfo": 1, "characterSecondaryInfo": 1}}])
    else:
        characters = mongo.db.characters.aggregate([{"$sample": {"size": sample_size}}, {"$project": {"characterImgSrc": {"$concat": [url_for('static', filename='characters-images/'), "$characterImgSrc"]}, "_id": 1, "characterName": 1, "characterMainInfo": 1, "characterSecondaryInfo": 1}}])

    response = json_util.dumps(characters)

    return make_response(response)

@app.route("/user/favorites/<string:userId>", methods = ['GET'])
def getFavorites(userId):
    user = mongo.db.users.find_one({"_id": ObjectId(userId)})
    userFavoriteCharacters = user["favoriteCharacters"]
    favoriteCharactersInfo = mongo.db.characters.find({'characterName': {'$in': userFavoriteCharacters}})
    return json_util.dumps(favoriteCharactersInfo)


@app.route("/characters/favorite/<string:characterName>", methods = ['POST'])
def addFavorite(characterName):
    loged_user = mongo.db.users.find_one({'_id': ObjectId(request.json["id"])})
    favorite_characters_in_db = loged_user['favoriteCharacters']
    favorite_characters_in_db.append(characterName)
    mongo.db.users.update_one({'_id': ObjectId(request.json["id"])}, {'$set': {'favoriteCharacters': favorite_characters_in_db}})

    return jsonify({"message": F'{characterName} added as favorite'})

@app.route("/characters/favorite/<string:characterName>", methods = ['PATCH'])
def removeFavorite(characterName):
    loged_user = mongo.db.users.find_one({'_id': ObjectId(request.json["id"])})
    favorite_characters_in_db = loged_user['favoriteCharacters']
    favorite_characters_in_db.remove(characterName)

    mongo.db.users.update_one({'_id': ObjectId(request.json["id"])}, {'$set': {'favoriteCharacters': favorite_characters_in_db}})

    return jsonify({"message": F'{characterName} remove from favorites'})

############## error handlers


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

################## TESTS

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

