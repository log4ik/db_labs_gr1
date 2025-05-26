from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    passwordHash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), nullable=False)
    isActive = db.Column(db.Boolean, nullable=False)

    surveys = db.relationship('Survey', backref='user', cascade='all, delete')

class Survey(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(50), nullable=False)
    creationDate = db.Column(db.DateTime, nullable=False)
    closeDate = db.Column(db.DateTime)
    userId = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    questions = db.relationship('Question', backref='survey', cascade='all, delete')
    links = db.relationship('SurveyLink', backref='survey', cascade='all, delete')

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(50), nullable=False)
    isRequired = db.Column(db.Boolean, nullable=False)
    order = db.Column(db.Integer, nullable=False)
    surveyId = db.Column(db.Integer, db.ForeignKey('survey.id'), nullable=False)

    answers = db.relationship('Answer', backref='question', cascade='all, delete')

class SurveyLink(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(100), unique=True, nullable=False)
    isActive = db.Column(db.Boolean, nullable=False)
    expiryDate = db.Column(db.DateTime)
    clicks = db.Column(db.Integer, default=0, nullable=False)
    surveyId = db.Column(db.Integer, db.ForeignKey('survey.id'), nullable=False)

    responses = db.relationship('Response', backref='survey_link', cascade='all, delete')

class Response(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    submissionDate = db.Column(db.DateTime, nullable=False)
    isComplete = db.Column(db.Boolean, nullable=False)
    surveyLinkId = db.Column(db.Integer, db.ForeignKey('survey_link.id'), nullable=False)

    answers = db.relationship('Answer', backref='response', cascade='all, delete')

class Answer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.Text, nullable=False)
    responseId = db.Column(db.Integer, db.ForeignKey('response.id'), nullable=False)
    questionId = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)
