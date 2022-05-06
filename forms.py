from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Email

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(Email(message=("Enter email please."))), Length(max=255)])
    password = PasswordField('Password', validators=[DataRequired(message=("Enter password please.")), Length(max=100)])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Login')

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(message=("Enter username please.")), Length(max=100)])
    email = StringField('Email', validators=[DataRequired(Email(message=("Enter email please."))), Length(max=255)])
    password = PasswordField('Password', validators=[DataRequired(message=("Enter password please.")), Length(max=100)])
    passwordconfirm = PasswordField('Password Again', validators=[DataRequired(message=("Enter again password please.")), Length(max=100)])
    submit = SubmitField('Sign Up')
