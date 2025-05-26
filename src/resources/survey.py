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
