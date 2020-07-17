import os
import joblib
import pandas as pd
import xgboost as xgb

from sklearn.preprocessing import MultiLabelBinarizer

from app import models


def get_skills():
    skills_data = pd.DataFrame(columns=['skills', 'profession'])
    profs = models.Profession.query.all()

    for prof in profs:
        prof_id = prof.id
        vacancies = list(models.Vacancy.query.filter_by(profession_id=prof_id))

        for vacancy in vacancies:
            skills_data = skills_data.append(
                {
                    'skills': [skill.id for skill in vacancy.skills],
                    'profession': prof_id
                },
                ignore_index=True
            )

    return skills_data


def get_classifier(data):
    if type(data) != pd.core.frame.DataFrame:
        raise TypeError('expected pandas DataFrame')

    if not ('skills' in data.columns and 'profession' in data.columns):
        raise ValueError("DataFrame should contain columns 'skills' and 'profession'")

    mlb = MultiLabelBinarizer()

    train = pd.DataFrame(mlb.fit_transform(data.skills), columns=mlb.classes_)

    classifier = xgb.XGBClassifier()
    classifier.fit(train, data.profession.astype('int'))

    return classifier


def update_classifier():
    skills = get_skills()
    clf = get_classifier(skills)
    joblib.dump(clf, os.path.join('serial', 'classifier.pkl'))


def get_profession(user_skills):
    if type(user_skills) != dict:
        raise TypeError('expected dict')

    clf = joblib.load(os.path.join('serial', 'classifier.pkl'))

    try:
        pred = clf.predict_proba(pd.DataFrame(user_skills, index=[0]))[0]
    except ValueError as e:
        if 'feature_names mismatch' in e.args[0]:
            raise ValueError('Feature names mismatch. Fix input data or update classifier') from None
        else:
            raise e

    return {idx + 1: val for idx, val in enumerate(pred)}
