from flask_wtf import FlaskForm
from wtforms import SubmitField, SelectField, TextAreaField, validators
from app.models import Profession


class SelectProf(FlaskForm):
    select = SelectField("Professions",
                choices=[prof.name for prof in Profession.query.all()])
    submit = SubmitField("Select")

class ProfPredict(FlaskForm):
    skills = TextAreaField('Enter your skills')
    submit = SubmitField("Enter")
