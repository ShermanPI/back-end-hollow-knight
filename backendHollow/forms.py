from backendHollow import mongo
from bson import json_util
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField,SubmitField, HiddenField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators = [DataRequired(), Length(min=2, max=12)])
    email = StringField('Email', validators = [DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo('password')])
    csrf_token = HiddenField("csrf_token")
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = mongo.db.users.find_one({"username": username.data})
        if user:
            raise ValidationError("That username is Taken. Please choose a diferent one")
    
    def validate_email(self, email):
        email = mongo.db.users.find_one({"email": email.data})
        if email:
            raise ValidationError("That email is Taken. Please choose a diferent one")

class LoginForm(FlaskForm):
    username = StringField('Username', validators = [DataRequired()])
    password = StringField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember me')
    csrf_token = HiddenField("csrf_token")
    submit = SubmitField('Log In')
