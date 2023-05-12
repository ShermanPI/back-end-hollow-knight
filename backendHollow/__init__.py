from flask import Flask, session
from flask_pymongo import PyMongo
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from datetime import timedelta
import os

app = Flask(__name__)

@app.before_request
def make_session_permanent():
    session.permanent = True

app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=30)
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = False
app.config['SESSION_COOKIE_SAMESITE'] = 'None'
CORS(app, supports_credentials=True)
SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY
app.config['MONGO_URI'] = "mongodb+srv://juokx1:ivhcJlPAiN1QnVsj@wikisherman.ewhecfi.mongodb.net/hollowDB?retryWrites=true&w=majority"
app.config['WTF_CSRF_ENABLED'] = False
mongo = PyMongo(app)
bcrypt = Bcrypt(app)

from backendHollow import routes
