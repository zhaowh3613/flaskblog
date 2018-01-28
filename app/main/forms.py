from flask_wtf import Form
from wtforms import StringField, SubmitField
from wtforms.validators import Required, Email, Length


class NameForm(Form):
    emial = StringField('Email', validators=[Required(), Length(1, 64), Email()])
    username = StringField('what is your name?', validators=[Required()])
    password = StringField('Password', validators=[Required(), Length(1, 64)])
    submit = SubmitField('submit')
