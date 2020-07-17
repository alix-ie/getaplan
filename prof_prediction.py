import os
import joblib
import pandas as pd
import xgboost as xgb

from sklearn.model_selection import train_test_split
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
    # todo: check data type, structure

    mlb = MultiLabelBinarizer()

    train = pd.DataFrame(mlb.fit_transform(data.skills), columns=mlb.classes_)

    X_train, X_test, y_train, y_test = train_test_split(train, data.profession.astype('int'), test_size=0.2)

    classifier = xgb.XGBClassifier()
    classifier.fit(X_train, y_train)

    joblib.dump(classifier, os.path.join('serial', 'classifier.pkl'))


def update_classifier():
    skills = get_skills()
    get_classifier(skills)


def get_profession(user_skills):
    # todo: check user_skills type

    clf = joblib.load(os.path.join('serial', 'classifier.pkl'))

    pred = clf.predict_proba(pd.DataFrame(user_skills, index=[0]))[0]
    # todo: ValueError msg

    return {idx + 1: val for idx, val in enumerate(pred)}
