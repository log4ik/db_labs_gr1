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
