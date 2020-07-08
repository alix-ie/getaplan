from app import app, db
from app.models import Profession, Skill, Vacancy


@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'Profession': Profession,
        'Skill': Skill,
        'Vacancy': Vacancy
    }
