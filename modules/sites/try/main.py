from flask import Blueprint
from flask_restful import Api, Resource

test = Blueprint('test', __name__, url_prefix='/test')
testapi = Api(test)


def jsonext(self):
    def wrapper(cls, *args, **kwargs):
        return cls
    return wrapper

# @jsonext
class TestApi(Resource):

    def get(self):
        return {'test': 0}


testapi.add_resource(TestApi, '/info')
