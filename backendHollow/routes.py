from flask import jsonify
from backendHollow import app, mongo
from backendHollow.forms import createCharacterForm
import secrets
from bson.objectid import ObjectId

def get_logged_user(request):
    if(request.cookies.get('logged_user_id', None)):
        user = mongo.db.users.find_one({'_id': ObjectId(request.cookies.get('logged_user_id'))})
        return user
    else:
        return None

@app.before_request
def setup():
    session.permanent = True

@app.route("/csrf_token", methods = ["GET"])
def csrf_token():
    token = secrets.token_hex(16)
    return jsonify({'csrfToken': token})


from backendHollow.handlers import character, user