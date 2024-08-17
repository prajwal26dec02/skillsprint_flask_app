from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, validators
from models import User

class RegistrationForm(FlaskForm):
    name = StringField('Name', [validators.DataRequired()])
    email = StringField('Email', [validators.DataRequired(), validators.Email()])
    password = PasswordField('Password', [validators.DataRequired()])
    confirm_password = PasswordField('Confirm Password', [
        validators.DataRequired(),
        validators.EqualTo('password', message='Passwords must match')
    ])
    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise validators.ValidationError('Email is already taken')

class LoginForm(FlaskForm):
    email = StringField('Email', [validators.DataRequired(), validators.Email()])
    password = PasswordField('Password', [validators.DataRequired()])
    def validate_email(self, field):
        user = User.query.filter_by(email=field.data).first()
        if user is None:
            raise validators.ValidationError('Email is not registered')
    def validate_password(self, field):
        user = User.query.filter_by(email=self.email.data).first()
        if user is not None and not user.check_password(field.data):
            raise validators.ValidationError('Incorrect password')