from flask import jsonify, session
from backendHollow import app
from backendHollow.forms import createCharacterForm
import secrets

@app.route("/csrf_token", methods = ["GET"])
def csrf_token():
    token = secrets.token_hex(16)
    session['form_csrf_token'] = token
    return jsonify({'csrfToken': token})


from backendHollow.handlers import character, user