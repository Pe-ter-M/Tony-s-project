from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SelectField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from app.models.user import User

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[
        DataRequired(),
        Length(min=3, max=64, message='Username must be between 3 and 64 characters.')
    ])
    email = StringField('Email', validators=[
        DataRequired(),
        Email(),
        Length(max=120)
    ])
    first_name = StringField('First Name', validators=[
        DataRequired(),
        Length(max=64)
    ])
    last_name = StringField('Last Name', validators=[
        DataRequired(),
        Length(max=64)
    ])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=6, message='Password must be at least 6 characters long.')
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match.')
    ])
    role = SelectField('Role', choices=User.get_role_choices(), validators=[DataRequired()])
    is_active = BooleanField('Active', default=True)
    submit = SubmitField('Create User')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Please use a different email address.')

class EditUserForm(RegistrationForm):
    submit = SubmitField('Update User')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.password.validators = [Length(min=6, message='Password must be at least 6 characters long.')]
        self.confirm_password.validators = [EqualTo('password', message='Passwords must match.')]