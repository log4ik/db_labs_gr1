from flask import Flask
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
api = Api(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///survey.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

from models import User, Survey, Question, SurveyLink, Response, Answer

from resources.survey import SurveyListResource, SurveyResource
from resources.question import QuestionListResource, QuestionResource
from resources.response import ResponseListResource, ResponseResource
from resources.answer import AnswerListResource, AnswerResource

api.add_resource(SurveyListResource, '/surveys')
api.add_resource(SurveyResource, '/surveys/<int:survey_id>')

api.add_resource(QuestionListResource, '/questions')
api.add_resource(QuestionResource, '/questions/<int:question_id>')

api.add_resource(ResponseListResource, '/responses')
api.add_resource(ResponseResource, '/responses/<int:response_id>')

api.add_resource(AnswerListResource, '/answers')
api.add_resource(AnswerResource, '/answers/<int:answer_id>')

@app.route('/')
def index():
    return {'message': 'Survey API is working!'}

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
