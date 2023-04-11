from backendHollow import mongo
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, PasswordField,SubmitField, HiddenField, BooleanField, TextAreaField, Field
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

class createCharacterForm(FlaskForm):
    characterName = StringField('Character Name', validators=[DataRequired(), Length(min=2, max=22)])
    characterMainInfo = TextAreaField("Character Main Info", validators=[DataRequired()])
    characterSecondaryInfo = TextAreaField("character Secondary Info")
    csrf_token = HiddenField("csrf_token")
    # characterImgSrc = Field('Character Image') # This doesnt work so im using the request.files to search my file submited validators=[FileRequired(), FileAllowed(['png', 'jpeg', 'webp', 'jpg'])]
    submit = SubmitField('Create')

    def validate_characterName(self, characterName):
        characterName = mongo.db.characters.find_one({"characterName": characterName.data})
        if characterName:
            raise ValidationError("That Character Name is Taken. Please choose a diferent one")