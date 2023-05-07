from flask import jsonify, session, make_response
from backendHollow import app
from backendHollow.forms import createCharacterForm
import secrets

@app.route("/csrf_token", methods = ["GET"])
def csrf_token():
    token = secrets.token_hex(16)
    session['form_csrf_token'] = token
    response = make_response(jsonify({'csrfToken': token}))
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response


from backendHollow.handlers import character, user