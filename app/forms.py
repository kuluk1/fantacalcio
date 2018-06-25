from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField, HiddenField
from wtforms.validators import DataRequired

class LoginForm(FlaskForm):
    name = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegisterForm(FlaskForm):
    name = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    money = HiddenField()
    submit = SubmitField('Register')

class BidForm(FlaskForm):
    bid = IntegerField('Amount', validators=[DataRequired()])
    user_id = HiddenField()
    player_id = HiddenField()
    submit = SubmitField('Bid')