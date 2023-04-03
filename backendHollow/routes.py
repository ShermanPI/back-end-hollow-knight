from flask import make_response, request, jsonify, session, render_template
from backendHollow import app, mongo, bcrypt
from backendHollow.forms import RegistrationForm, LoginForm
from bson import json_util
from bson.objectid import ObjectId
import secrets

@app.route("/csrf_token", methods = ["GET"])
def csrf_token():
    token = secrets.token_hex(16)
    session['form_csrf_token'] = token
    return jsonify({'csrfToken': token})

@app.route("/register", methods = ["POST"])
def register_user():
    print("WUO WUOWUWOWUOW WUOWUWO", session)
    form = RegistrationForm(request.form)
    print("EA EA EASSASSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSXAS: ", form.csrf_token.data, session["form_csrf_token"])
    if(form.csrf_token.data == session["form_csrf_token"]):
        if(form.validate_on_submit()):
            username = form.username.data
            email = form.email.data
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode("utf-8")

            user = mongo.db.users.insert_one({'username': username, 'email': email, 'password': hashed_password, 'pfpId': 0, 'HScore': 0, 'unlockByTheUser': 0, 'type': "user"})

            return jsonify({
                    'message': f'Account for <span class="points-required">{form.username.data}</span> has been created... Now you can Log In',
                    'userData': {
                        'id': str(user.inserted_id), 
                        'username': form.username.data,
                        'email': form.email.data
                    }
                })
        else:
            response = make_response(jsonify({'errors': form.errors}))
            response.status_code = 409

            return response
    else:
        return forbidden()
    


@app.route("/login", methods = ["POST"])
def login_user():
    form = LoginForm(request.form)
    if(form.csrf_token.data == session.get("form_csrf_token")):
        if form.validate_on_submit():
            user = mongo.db.users.find_one({'username': form.username.data})

            if user and bcrypt.check_password_hash(user['password'], form.password.data):
                if form.remember.data:
                    session['loged_user'] = json_util.dumps(user)

                return jsonify({
                    'message': f"User {form.username.data} has been Loged In",
                    'userData': {
                        "id": str(user["_id"]),
                        "username": user["username"],
                        "pfpId": user["pfpId"],
                        "HScore": user["HScore"],
                        "unlockByTheUser": user["unlockByTheUser"]
                        }
                })
            else:

                response = make_response(jsonify({'errors': {'username': 'Login Unsusccesful. Please check username and password'}}))
                response.status_code = 401
                return response
        else:
            return bad_request()
    else:
        return forbidden()


@app.route("/login", methods = ["GET"])
def loged_user():
    if 'loged_user' in session:
        user = session['loged_user']
        return user
    
    return jsonify({
        'user': {}
        })

@app.route('/logout')
def logout():
    session.pop('loged_user', None)
    return jsonify({'message': 'The user logged out'})

@app.route("/users", methods = ["GET"])
def get_users():
    users_bson = mongo.db.users.find()
    users = json_util.dumps(users_bson)
    return make_response(users, mimetype="application/json")

@app.route("/", methods = ['POST', 'GET'])
def index():
    form = LoginForm()
    if form.validate_on_submit():
        print(f'ea {form.username.data} \n {form.email.data} \n {form.hidden_tag()}')
    else:
        print(f'No se pudo validar {form.errors}')

    return render_template("index.html", form = form)


@app.route("/characters", methods=['POST'])
def addCharacter():
    payload = request.json

    characterImgSrc = payload.get('imgSrc', "")
    characterName = payload.get('name', "")
    characterMainInfo = payload.get('mainInfo', "")
    characterSecondaryInfo = payload.get('secondaryInfo', "")

    if characterImgSrc and characterName and characterMainInfo:
        id = mongo.db.characters.insert_one(
            {"imgSrc": characterImgSrc, "name": characterName, "mainInfo": characterMainInfo, "secondaryInfo": characterSecondaryInfo}
        )
        
        response = {
            "message": "Character created succesfully",
            "status": "success",
            "data": {
                "id": str(id.inserted_id),
                "name": characterName,
                "imgSrc": characterImgSrc,
                "mainInfo": characterMainInfo,
                "secondaryInfo": characterSecondaryInfo
            }
        } 

        return jsonify(response)
    else:
        return bad_request()

@app.route("/characters", methods = ['GET'])
def getCharacters():
    characters = mongo.db.characters.find() #returns a BSON, and its a cursor
    response = json_util.dumps(characters)

    return make_response(response, mimetype="application/json")

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
def updateUser(id):
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