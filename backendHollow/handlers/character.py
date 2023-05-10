import secrets
import os
from flask import make_response, request, jsonify, session, url_for
from backendHollow import app, mongo
from backendHollow.forms import createCharacterForm, editCharacterForm
from bson import json_util
from bson.objectid import ObjectId
from google.cloud import storage

CLOUD_STORAGE_BUCKET = 'hollow-images'
os.environ["GCLOUD_PROJECT"] = "backendhollow"
gcs = storage.Client()
bucket = gcs.get_bucket(CLOUD_STORAGE_BUCKET)

def save_picture(form_picture, prev_img = False):
    
    if(prev_img):
        prev_picture = bucket.blob(prev_img)
        if prev_picture.exists():
            prev_picture.delete()

    random_hex = secrets.token_hex(8)
    _, f_extention = os.path.splitext(form_picture.filename)
    picture_filename = random_hex + f_extention

    blob = bucket.blob(picture_filename)

    blob.upload_from_string(
        form_picture.read(), content_type=form_picture.content_type
    )

    blob.make_public()
    return blob.public_url

def delete_picture(picture):
    picture_blob = bucket.blob(picture)
    if picture_blob.exists():
        picture_blob.delete()

def isAdmin():
    user = mongo.db.users.find_one({"_id": ObjectId(session['loged_user'])}, {'password': 0})
    if user['type'] == 'admin':
        return True
    else:
        return False

@app.route("/characters", methods = ["POST"])
def addCharacter():
    form = createCharacterForm(request.form)
    
    if(form.csrf_token.data == session.get("form_csrf_token") and isAdmin()):
        if(form.validate_on_submit()):
            picture_file = save_picture(request.files['characterImgSrc'])

            newCharacter = mongo.db.characters.insert_one({'characterName': form.characterName.data.strip(), 'characterMainInfo': form.characterMainInfo.data, 'characterSecondaryInfo': form.characterSecondaryInfo.data, 'characterImgSrc': picture_file})
            character = mongo.db.characters.find_one({'_id': ObjectId(newCharacter.inserted_id)})
            # character['characterImgSrc'] = f"{url_for('static', filename='characters-images/')}{character['characterImgSrc']}"
            return json_util.dumps(character)
        else:
            response = make_response(jsonify({'errors': form.errors}))
            response.status_code = 409

            return response
    else:
        return forbidden()

@app.route("/characters", methods = ['GET'])
def getCharacters():
    characters = mongo.db.characters.aggregate([{"$project": {"characterImgSrc": {"$concat": ["$characterImgSrc"]}, "_id": 1, "characterName": 1, "characterMainInfo": 1, "characterSecondaryInfo": 1}}])
    response = json_util.dumps(characters)

    return make_response(response)

@app.route("/character/<characterName>", methods = ['PUT'])
def updateCharacter(characterName):
    form = editCharacterForm(request.form)

    if(form.csrf_token.data == session.get("form_csrf_token") and isAdmin()):
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
        characters = mongo.db.characters.aggregate([{"$match": {"_id": {"$nin": already_rendered}}}, {"$sample": {"size": sample_size}}, {"$project": {"characterImgSrc": {"$concat": ["$characterImgSrc"]}, "_id": 1, "characterName": 1, "characterMainInfo": 1, "characterSecondaryInfo": 1}}])
    else:
        characters = mongo.db.characters.aggregate([{"$sample": {"size": sample_size}}, {"$project": {"characterImgSrc": {"$concat": ["$characterImgSrc"]}, "_id": 1, "characterName": 1, "characterMainInfo": 1, "characterSecondaryInfo": 1}}])

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

@app.route('/character/<id>', methods = ['DELETE'])
def deleteCharacter(id):
    if(isAdmin()):
        character_to_delete = mongo.db.characters.find_one({'_id': ObjectId(id)})
        if(character_to_delete):
            mongo.db.characters.delete_one({'_id': ObjectId(id)})
            delete_picture(character_to_delete['characterImgSrc'])
            return jsonify({'message': 'Character deleted'})
        else:
            response = make_response(jsonify({'message': 'There is no character with this name, please check and try again'}))
            response.status_code = 404
            return response
    
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