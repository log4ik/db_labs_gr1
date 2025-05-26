# Реалізація інформаційного та програмного забезпечення

У рамках проєкту розробляється:
- SQL-скрипти для створення та початкового наповнення бази даних;
- RESTfull сервіс для управління даними.


## SQL-скрипти
### main.sql
```sql
  CREATE TABLE User (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    passwordHash VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL,
    isActive BOOLEAN NOT NULL
);

CREATE TABLE Survey (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(50) NOT NULL,
    creationDate DATETIME NOT NULL,
    closeDate DATETIME,
    userId INT NOT NULL,
    FOREIGN KEY (userId) REFERENCES User(id) ON DELETE CASCADE
);

CREATE TABLE Question (
    id INT AUTO_INCREMENT PRIMARY KEY,
    text TEXT NOT NULL,
    type VARCHAR(50) NOT NULL,
    isRequired BOOLEAN NOT NULL,
    `order` INT NOT NULL,
    surveyId INT NOT NULL,
    FOREIGN KEY (surveyId) REFERENCES Survey(id) ON DELETE CASCADE
);

CREATE TABLE SurveyLink (
    id INT AUTO_INCREMENT PRIMARY KEY,
    token VARCHAR(100) NOT NULL UNIQUE,
    isActive BOOLEAN NOT NULL,
    expiryDate DATETIME,
    clicks INT NOT NULL DEFAULT 0,
    surveyId INT NOT NULL,
    FOREIGN KEY (surveyId) REFERENCES Survey(id) ON DELETE CASCADE
);

CREATE TABLE Response (
    id INT AUTO_INCREMENT PRIMARY KEY,
    submissionDate DATETIME NOT NULL,
    isComplete BOOLEAN NOT NULL,
    surveyLinkId INT NOT NULL,
    FOREIGN KEY (surveyLinkId) REFERENCES SurveyLink(id) ON DELETE CASCADE
);

CREATE TABLE Answer (
    id INT AUTO_INCREMENT PRIMARY KEY,
    value TEXT NOT NULL,
    responseId INT NOT NULL,
    questionId INT NOT NULL,
    FOREIGN KEY (responseId) REFERENCES Response(id) ON DELETE CASCADE,
    FOREIGN KEY (questionId) REFERENCES Question(id) ON DELETE CASCADE
);
```

### test_d.sql
```sql
  INSERT INTO User (email, passwordHash, role, isActive) VALUES
('admin@example.com', 'hash1', 'admin', TRUE),
('user1@example.com', 'hash2', 'respondent', TRUE),
('user2@example.com', 'hash3', 'respondent', TRUE);

INSERT INTO Survey (title, description, status, creationDate, closeDate, userId) VALUES
('Customer Satisfaction Survey', 'Tell us about your experience.', 'active', NOW(), NULL, 1),
('Product Feedback', 'We value your thoughts on our new product.', 'draft', NOW(), NULL, 1),
('Website Usability', 'How easy is it to use our website?', 'active', NOW(), NULL, 1);

INSERT INTO Question (text, type, isRequired, `order`, surveyId) VALUES
-- Survey 1
('How satisfied are you?', 'rating', TRUE, 1, 1),
('What can we improve?', 'text', FALSE, 2, 1),
-- Survey 2
('Is the product useful?', 'yesno', TRUE, 1, 2),
('Would you recommend it?', 'yesno', TRUE, 2, 2),
-- Survey 3
('Was the site easy to navigate?', 'yesno', TRUE, 1, 3),
('Any technical issues?', 'text', FALSE, 2, 3);

INSERT INTO SurveyLink (token, isActive, expiryDate, clicks, surveyId) VALUES
('link1', TRUE, DATE_ADD(NOW(), INTERVAL 10 DAY), 5, 1),
('link2', TRUE, DATE_ADD(NOW(), INTERVAL 5 DAY), 0, 1),
('link3', TRUE, DATE_ADD(NOW(), INTERVAL 15 DAY), 2, 2),
('link4', TRUE, DATE_ADD(NOW(), INTERVAL 7 DAY), 1, 3);

INSERT INTO Response (submissionDate, isComplete, surveyLinkId) VALUES
(NOW(), TRUE, 1),
(NOW(), TRUE, 2),
(NOW(), FALSE, 3),
(NOW(), TRUE, 4);

-- Response 1 (link1, survey 1)
INSERT INTO Answer (value, responseId, questionId) VALUES
('4', 1, 1),
('More options needed.', 1, 2);

-- Response 2 (link2, survey 1)
INSERT INTO Answer (value, responseId, questionId) VALUES
('5', 2, 1),
('Nothing to improve.', 2, 2);

-- Response 3 (link3, survey 2) — incomplete, only one answer
INSERT INTO Answer (value, responseId, questionId) VALUES
('Yes', 3, 3);

-- Response 4 (link4, survey 3)
INSERT INTO Answer (value, responseId, questionId) VALUES
('Yes', 4, 5),
('No issues', 4, 6);
```

## RESTfull сервіс для управління даними
### Ресурси
```py
from flask_restful import Resource, reqparse
from models import db, User

parser = reqparse.RequestParser()
parser.add_argument('email', required=True)
parser.add_argument('passwordHash', required=True)
parser.add_argument('role', required=True)
parser.add_argument('isActive', type=bool, required=True)

class UserListResource(Resource):
    def get(self):
        users = User.query.all()
        return [{'id': u.id, 'email': u.email, 'role': u.role, 'isActive': u.isActive} for u in users]

    def post(self):
        args = parser.parse_args()
        user = User(**args)
        db.session.add(user)
        db.session.commit()
        return {'message': 'User created', 'id': user.id}, 201

class UserResource(Resource):
    def get(self, user_id):
        user = User.query.get_or_404(user_id)
        return {'id': user.id, 'email': user.email, 'role': user.role, 'isActive': user.isActive}

    def put(self, user_id):
        user = User.query.get_or_404(user_id)
        args = parser.parse_args()
        for key, value in args.items():
            setattr(user, key, value)
        db.session.commit()
        return {'message': 'User updated'}

    def delete(self, user_id):
        user = User.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        return {'message': 'User deleted'}
```

```py
from flask_restful import Resource, reqparse
from models import db, Survey
from datetime import datetime

parser = reqparse.RequestParser()
parser.add_argument('title', required=True)
parser.add_argument('description')
parser.add_argument('status', required=True)
parser.add_argument('creationDate', required=False, default=datetime.utcnow)
parser.add_argument('closeDate')
parser.add_argument('userId', type=int, required=True)

class SurveyListResource(Resource):
    def get(self):
        surveys = Survey.query.all()
        return [{
            'id': s.id,
            'title': s.title,
            'status': s.status,
            'userId': s.userId
        } for s in surveys]

    def post(self):
        args = parser.parse_args()
        survey = Survey(
            title=args['title'],
            description=args['description'],
            status=args['status'],
            creationDate=datetime.utcnow(),
            closeDate=args['closeDate'],
            userId=args['userId']
        )
        db.session.add(survey)
        db.session.commit()
        return {'message': 'Survey created', 'id': survey.id}, 201

class SurveyResource(Resource):
    def get(self, survey_id):
        s = Survey.query.get_or_404(survey_id)
        return {
            'id': s.id,
            'title': s.title,
            'description': s.description,
            'status': s.status,
            'creationDate': s.creationDate.isoformat(),
            'closeDate': s.closeDate.isoformat() if s.closeDate else None,
            'userId': s.userId
        }

    def delete(self, survey_id):
        s = Survey.query.get_or_404(survey_id)
        db.session.delete(s)
        db.session.commit()
        return {'message': 'Survey deleted'}
```

```py
from flask_restful import Resource, reqparse
from models import db, Question

parser = reqparse.RequestParser()
parser.add_argument('text', required=True)
parser.add_argument('type', required=True)
parser.add_argument('isRequired', type=bool, required=True)
parser.add_argument('order', type=int, required=True)
parser.add_argument('surveyId', type=int, required=True)

class QuestionListResource(Resource):
    def get(self):
        questions = Question.query.all()
        return [{
            'id': q.id,
            'text': q.text,
            'type': q.type,
            'isRequired': q.isRequired,
            'order': q.order,
            'surveyId': q.surveyId
        } for q in questions]

    def post(self):
        args = parser.parse_args()
        q = Question(**args)
        db.session.add(q)
        db.session.commit()
        return {'message': 'Question created', 'id': q.id}, 201

class QuestionResource(Resource):
    def get(self, question_id):
        q = Question.query.get_or_404(question_id)
        return {
            'id': q.id,
            'text': q.text,
            'type': q.type,
            'isRequired': q.isRequired,
            'order': q.order,
            'surveyId': q.surveyId
        }

    def delete(self, question_id):
        q = Question.query.get_or_404(question_id)
        db.session.delete(q)
        db.session.commit()
        return {'message': 'Question deleted'}
```

```py
from flask_restful import Resource, reqparse
from models import db, Response
from datetime import datetime

parser = reqparse.RequestParser()
parser.add_argument('submissionDate', required=False, default=datetime.utcnow)
parser.add_argument('isComplete', type=bool, required=True)
parser.add_argument('surveyLinkId', type=int, required=True)

class ResponseListResource(Resource):
    def get(self):
        responses = Response.query.all()
        return [{
            'id': r.id,
            'submissionDate': r.submissionDate.isoformat(),
            'isComplete': r.isComplete,
            'surveyLinkId': r.surveyLinkId
        } for r in responses]

    def post(self):
        args = parser.parse_args()
        r = Response(
            submissionDate=datetime.utcnow(),
            isComplete=args['isComplete'],
            surveyLinkId=args['surveyLinkId']
        )
        db.session.add(r)
        db.session.commit()
        return {'message': 'Response created', 'id': r.id}, 201

class ResponseResource(Resource):
    def get(self, response_id):
        r = Response.query.get_or_404(response_id)
        return {
            'id': r.id,
            'submissionDate': r.submissionDate.isoformat(),
            'isComplete': r.isComplete,
            'surveyLinkId': r.surveyLinkId
        }

    def delete(self, response_id):
        r = Response.query.get_or_404(response_id)
        db.session.delete(r)
        db.session.commit()
        return {'message': 'Response deleted'}
```

```py
from flask_restful import Resource, reqparse
from models import db, Answer

parser = reqparse.RequestParser()
parser.add_argument('value', required=True)
parser.add_argument('responseId', type=int, required=True)
parser.add_argument('questionId', type=int, required=True)

class AnswerListResource(Resource):
    def get(self):
        answers = Answer.query.all()
        return [{
            'id': a.id,
            'value': a.value,
            'responseId': a.responseId,
            'questionId': a.questionId
        } for a in answers]

    def post(self):
        args = parser.parse_args()
        a = Answer(**args)
        db.session.add(a)
        db.session.commit()
        return {'message': 'Answer created', 'id': a.id}, 201

class AnswerResource(Resource):
    def get(self, answer_id):
        a = Answer.query.get_or_404(answer_id)
        return {
            'id': a.id,
            'value': a.value,
            'responseId': a.responseId,
            'questionId': a.questionId
        }

    def delete(self, answer_id):
        a = Answer.query.get_or_404(answer_id)
        db.session.delete(a)
        db.session.commit()
        return {'message': 'Answer deleted'}
```

### app.py
```py
from flask import Flask
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
api = Api(app)

# Налаштування бази даних (заміни URI при потребі)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///survey.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Імпорт моделей
from models import User, Survey, Question, SurveyLink, Response, Answer

# Імпорт ресурсів
from resources.survey import SurveyListResource, SurveyResource
from resources.question import QuestionListResource, QuestionResource
from resources.response import ResponseListResource, ResponseResource
from resources.answer import AnswerListResource, AnswerResource

# Маршрути REST API
api.add_resource(SurveyListResource, '/surveys')
api.add_resource(SurveyResource, '/surveys/<int:survey_id>')

api.add_resource(QuestionListResource, '/questions')
api.add_resource(QuestionResource, '/questions/<int:question_id>')

api.add_resource(ResponseListResource, '/responses')
api.add_resource(ResponseResource, '/responses/<int:response_id>')

api.add_resource(AnswerListResource, '/answers')
api.add_resource(AnswerResource, '/answers/<int:answer_id>')

# Головна сторінка (опціонально)
@app.route('/')
def index():
    return {'message': 'Survey API is working!'}

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Створює всі таблиці
    app.run(debug=True)
```

### models.py - Моделі БД
```py
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
```
