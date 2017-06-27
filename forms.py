from flask_wtf import FlaskForm
from wtforms import validators, StringField
from wtforms.validators import InputRequired


class FHIR_form(FlaskForm):
    resource_id = StringField('Resource ID: ', [validators.DataRequired()])


class MusicianForm(FlaskForm):
    name = StringField("Enter name of artist: ", validators=[InputRequired(message='Artist name is required')])
