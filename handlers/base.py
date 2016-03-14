from flask_restful import Resource, reqparse
from models import DictionnaryQueries

class BaseHandler(Resource):

    def __init__(self):
            """The constructor for this abstract class just creates a request_parser"""
            super().__init__()
            self.reqparse = reqparse.RequestParser()

    def do_request_parsing(self):
        self.args = self.reqparse.parse_args()

    def get(self):

        return {"status": "Correc'"}


class SearchTermsHandler(BaseHandler):

    def post(self):
        self.reqparse.add_argument("searchstring", required=True, type=str)
        self.do_request_parsing()
        return DictionnaryQueries().search_for_terms(self.args["searchstring"])