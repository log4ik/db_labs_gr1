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
