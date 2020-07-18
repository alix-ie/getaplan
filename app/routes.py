from app import app, db
from flask import render_template, redirect, flash, url_for, request
from app.forms import SelectProf, ProfPredict
from app.models import Profession, Skill, Vacancy
from sqlalchemy import func, desc
from prof_prediction import get_profession


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    form = SelectProf()
    if request.method == 'POST':
        return redirect(url_for("profession", name=form.select.data))
    return render_template("index.html", title="Select proffesion", form=form)


@app.route('/profession/<name>')
def profession(name):
    profession = Profession.query.filter_by(name=name).first_or_404()
    query = db.session.query(Skill.name, func.count(Vacancy.id).label('total')).join(Skill.vacancies).filter(Vacancy.profession_id == profession.id).group_by(Skill.id).order_by(desc('total')).limit(10).all()

    return render_template(
        'profession.html',
        profession=profession,
        labels=[skill.name for skill in query],
        values=[skill.total for skill in query],
        max=round(query[0].total, -2) + 100
    )


@app.route('/prof_prediction', methods=['GET', 'POST'])
def prof_prediction():
    form = ProfPredict()
    if request.method == 'POST':
        return redirect(url_for("predict_result", user_skills=form.skills.data))
    return render_template("prof_prediction.html", title="Profession prediction", form=form)


@app.route('/prof_prediction/result/<user_skills>')
def predict_result(user_skills):
    db_skills = db.session.query(Skill).all()
    dict_skills = {skill.id:0 for skill in db_skills}

    user_skills = user_skills.split(',')
    for u_skill in user_skills:
        query = db.session.query(Skill).filter(func.lower(Skill.name)==u_skill.lower()).first()
        if query:
            dict_skills[query.id] = 1

    professions = db.session.query(Profession).all()
    predictions = get_profession(dict_skills)
    ready_pred = {}
    for pred in predictions.keys():
        for prof in professions:
            percentage = int(round(predictions[pred], 2)*100)
            if int(pred) == prof.id and percentage >= 10:
                ready_pred[prof.name] = percentage
            if not ready_pred:
                ready_pred = 0
    return render_template("pred_result.html", title="Result", prediction=ready_pred )
