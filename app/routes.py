from app import app
from flask import render_template, redirect, flash, url_for
from app.forms import SearchProffForm


@app.route('/')
@app.route('/index', methods=['GET', 'POST'])
def index():
    form = SearchProffForm()
    if form.validate_on_submit():
        flash("Ваш {} запрос принят".format(form.profession_q.data))
        return redirect(url_for('index'))
    return render_template("index.html", title="Skills search", form=form)