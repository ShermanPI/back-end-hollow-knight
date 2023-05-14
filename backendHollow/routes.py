from flask import jsonify
from backendHollow import app
from backendHollow.forms import createCharacterForm
import secrets

@app.route("/csrf_token", methods = ["GET"])
def csrf_token():
    token = secrets.token_hex(16)
    return jsonify({'csrfToken': token})


from backendHollow.handlers import character, user