from flask import make_response, request, jsonify, session
from backendHollow import app, mongo, bcrypt
from backendHollow.forms import RegistrationForm, LoginForm
from bson import json_util
from bson.objectid import ObjectId


@app.route("/register", methods = ["POST"])
def register_user():
    form = RegistrationForm(request.form)
    if(form.csrf_token.data == session["form_csrf_token"]):
        if(form.validate_on_submit()):
            username = form.username.data
            email = form.email.data
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode("utf-8")

            user = mongo.db.users.insert_one({'username': username, 'email': email, 'password': hashed_password, 'pfpId': 0, 'HScore': 0, 'unlockByTheUser': 0, 'type': "user", 'favoriteCharacters': []})

            return jsonify({
                    'message': f'Account for <span class="points-required">{form.username.data}</span> has been created... Now you can Log In',
                    'userData': {
                        'id': str(user.inserted_id), 
                        'username': form.username.data
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
                user = mongo.db.users.find_one({'username': form.username.data}, {'password': 0})
                if form.remember.data:
                    session['loged_user'] = str(user['_id'])
                    print(json_util.dumps(user))

                return json_util.dumps(user)
            
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
    print("LOGEEEEEEED", session) 
    if 'loged_user' in session:
        user = mongo.db.users.find_one({"_id": ObjectId(session['loged_user'])})#save a JSON with the user data
        
        return json_util.dumps(user)
    else:
        return jsonify({
            'user': {}
            })

@app.route('/logout')
def logout():
    session.pop('loged_user', None)
    return jsonify({'message': 'The user logged out'})

@app.route("/user/<id>", methods=['GET'])
def getUser(id):
    user = mongo.db.users.find_one({"_id": ObjectId(id)}, {'password': 0})
    return json_util.dumps(user)

@app.route("/user/<id>", methods=['PUT']) #edit profile
def update_user(id):
    payload = request.json
    user = mongo.db.users.find_one({"_id": ObjectId(id)})

    if(payload.get("username", None)):
        userFinded = mongo.db.users.find_one({"username": payload.get("username")})

        if(userFinded):
            return jsonify({"message": "This username is already in Use. Please choose another one"}), 409
    
    if(payload.get("email", None)):
        emailFinded = mongo.db.users.find_one({"email": payload.get("email", None)})
        if(emailFinded):
            return jsonify({"message": "This email is already in Use. Please choose another one"}), 409

    user_username = payload.get("username", user["username"])
    user_email = payload.get("email", user["email"])
    user_pfp_id = payload.get("pfpId", user["pfpId"])
    user_HScore = payload.get("HScore", user["HScore"])
    user_unlocklByTheUser = payload.get("unlockByTheUser", user["unlockByTheUser"])
    user_type =  payload.get("type", user["type"])

    mongo.db.users.update_one({"_id": ObjectId(id)}, {"$set": {"username": user_username, "email": user_email, "pfpId": user_pfp_id, "HScore": user_HScore, "unlockByTheUser": user_unlocklByTheUser, "type": user_type}})
    user = mongo.db.users.find_one({"_id": ObjectId(id)})
    session['loged_user'] = session['loged_user'] = str(user['_id'])

    return json_util.dumps(user)

@app.route("/users", methods = ["GET"])
def get_users():
    users_bson = mongo.db.users.find({}, {'password': 0, 'email': 0})
    users = json_util.dumps(users_bson)
    return make_response(users, mimetype="application/json")

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