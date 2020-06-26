from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

class SearchProffForm(FlaskForm):
    profession_q = StringField("Поиск профессии", validators=[DataRequired()], render_kw={"class":"form-control"})
    submit = SubmitField("Найти!", render_kw={"class":"btn btn-primary"})