from flask import Flask, session
from flask_pymongo import PyMongo
from flask_cors import CORS
from flask_bcrypt import Bcrypt

app = Flask(__name__)
CORS(app, supports_credentials=True)
app.secret_key = 'de0b6d1205e578d7d79857e211e48182f8167878f4f6ad4b8cf6a7b447cab84c'
app.config['MONGO_URI'] = "mongodb://127.0.0.1:27017/hollowDB"
app.config['WTF_CSRF_ENABLED'] = False
mongo = PyMongo(app)
bcrypt = Bcrypt(app)

from backendHollow import routes
