import secrets
import os
import json
from flask import make_response, request, jsonify, session, url_for
from backendHollow import app, mongo
from backendHollow.forms import createCharacterForm, editCharacterForm
from bson import json_util
from bson.objectid import ObjectId


def save_picture(form_picture, prev_img = False):
    if(prev_img):
        prev_picture = os.path.join(app.root_path, 'static/characters-images', prev_img)
        if os.path.exists(prev_picture):
            os.remove(prev_picture)

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

            newCharacter = mongo.db.characters.insert_one({'characterName': form.characterName.data.strip(), 'characterMainInfo': form.characterMainInfo.data, 'characterSecondaryInfo': form.characterSecondaryInfo.data, 'characterImgSrc': picture_file})
            character = mongo.db.characters.find_one({'_id': ObjectId(newCharacter.inserted_id)})
            character['characterImgSrc'] = f"{url_for('static', filename='characters-images/')}{character['characterImgSrc']}"
            return json_util.dumps(character)
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

@app.route("/character/<characterName>", methods = ['PUT'])
def updateCharacter(characterName):
    form = editCharacterForm(request.form)

    if(form.csrf_token.data == session.get("form_csrf_token")):
        if(form.validate_on_submit()):
            new_character_info = {}
            character_to_edit = mongo.db.characters.find_one({'characterName': characterName})

            image = request.files['newCharacterImgSrc']
            if(image.filename):
                picture_file = save_picture(request.files['newCharacterImgSrc'], character_to_edit['characterImgSrc'])
                new_character_info['characterImgSrc'] = picture_file

            new_character_info['characterName'] = form.newCharacterName.data
            new_character_info['characterMainInfo'] = form.newCharacterMainInfo.data
            new_character_info['characterSecondaryInfo'] = form.newCharacterSecondaryInfo.data

            mongo.db.characters.update_one({"characterName": characterName}, {'$set': new_character_info})

            updated_characters = mongo.db.characters.find_one({"_id": ObjectId(str(character_to_edit['_id']))})
            updated_characters['characterImgSrc'] = f"{url_for('static', filename='characters-images/')}{updated_characters['characterImgSrc']}"
            return json_util.dumps(updated_characters)
        else:
            response = make_response(jsonify({'errors': form.errors}))
            response.status_code = 409
            return response
    else:
        return forbidden()

@app.route("/charactersSample/<int:sample_size>", methods = ['GET', 'POST'])
def getCharactersSample(sample_size):
    if request.method == 'POST':
        already_rendered = [ObjectId(id) for id in request.json['items']]
        print(already_rendered)
        characters = mongo.db.characters.aggregate([{"$match": {"_id": {"$nin": already_rendered}}}, {"$sample": {"size": sample_size}}, {"$project": {"characterImgSrc": {"$concat": [url_for('static', filename='characters-images/'), "$characterImgSrc"]}, "_id": 1, "characterName": 1, "characterMainInfo": 1, "characterSecondaryInfo": 1}}])
    else:
        characters = mongo.db.characters.aggregate([{"$sample": {"size": sample_size}}, {"$project": {"characterImgSrc": {"$concat": [url_for('static', filename='characters-images/'), "$characterImgSrc"]}, "_id": 1, "characterName": 1, "characterMainInfo": 1, "characterSecondaryInfo": 1}}])

    response = json_util.dumps(characters)

    return make_response(response)

@app.route("/user/favorites/<userId>", methods = ['GET'])
def getFavorites(userId):
    user = mongo.db.users.find_one({"_id": ObjectId(userId)})
    userFavoriteCharacters = user["favoriteCharacters"]
    favoriteCharactersInfo = mongo.db.characters.find({'_id': {'$in': userFavoriteCharacters}})
    return json_util.dumps(favoriteCharactersInfo)

@app.route("/<userId>/favorite/<characterName>", methods = ['POST'])
def addFavorite(userId, characterName):
    favorite_character = mongo.db.characters.find_one({"characterName": characterName})
    characterId = favorite_character["_id"]
    mongo.db.users.update_one({'_id': ObjectId(userId)}, {'$push': {'favoriteCharacters': ObjectId(characterId)}})    
    return jsonify({"message": F'{characterName} added as favorite'})

@app.route("/<userId>/favorite/<characterName>", methods = ['DELETE'])
def removeFavorite(userId, characterName):
    favorite_character = mongo.db.characters.find_one({"characterName": characterName})
    characterId = favorite_character["_id"]
    mongo.db.users.update_one({'_id': ObjectId(userId)}, {'$pull': {'favoriteCharacters': ObjectId(characterId)}})    

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