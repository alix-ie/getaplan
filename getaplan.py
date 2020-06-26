from app import app, db
from app.models import Profession, Area, Expirience, Skill, Vacancy

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db, 
        'Proffesion': Profession, 
        'Area': Area, 
        'Expirience': Expirience, 
        'Skill': Skill, 
        'Vacancy': Vacancy, 
        }