import pandas as pd
import xgboost as xgb
from sklearn.preprocessing import MultiLabelBinarizer

import pickle
from bson.binary import Binary
from datetime import datetime

from app import models
from mdb_connection import create_connection


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
    
    client = create_connection()

    try:
        db = client.get_database('getaplan')
        collection = db.models
        model_binary = pickle.dumps(clf)

        collection.replace_one(
            {'name': 'Classifier'},
            {
                'name': 'Classifier',
                'serialized': Binary(model_binary),
                'update': datetime.now()
            },
            upsert=True
        )
    finally:
        client.close()


def get_profession(user_skills):
    if type(user_skills) != dict:
        raise TypeError('expected dict')

    client = create_connection()

    try:
        db = client.get_database('getaplan')
        collection = db.models
        document = collection.find_one({'name': 'Classifier'})

        assert document
        clf = pickle.loads(document['serialized'])
    except AssertionError:
        raise FileNotFoundError('Classifier was not found') from None
    finally:
        client.close()

    try:
        pred = clf.predict_proba(pd.DataFrame(user_skills, index=[0]))[0]
    except ValueError as e:
        if 'feature_names mismatch' in e.args[0]:
            raise ValueError('Feature names mismatch. Fix input data or update classifier') from None
        else:
            raise e

    return {idx + 1: val for idx, val in enumerate(pred)}
