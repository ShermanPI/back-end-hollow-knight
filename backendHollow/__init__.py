from flask import Flask
from flask_pymongo import PyMongo


app = Flask(__name__)
app.secret_key = 'de0b6d1205e578d7d79857e211e48182f8167878f4f6ad4b8cf6a7b447cab84c'
app.config['MONGO_URI'] = "mongodb://127.0.0.1:27017/hollowDB"
mongo = PyMongo(app)

from backendHollow import routes
