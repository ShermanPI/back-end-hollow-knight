from flask import jsonify, session, render_template
from backendHollow import app
import secrets

@app.route("/csrf_token", methods = ["GET"])
def csrf_token():
    token = secrets.token_hex(16)
    session['form_csrf_token'] = token
    return jsonify({'csrfToken': token})


@app.route("/", methods = ['POST', 'GET'])
def index():
    return "NOTHING HERE"

from backendHollow.handlers import character, user