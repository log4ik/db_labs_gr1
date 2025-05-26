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
