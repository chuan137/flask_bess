from flask import Blueprint
from flask_restful import Api
from .api import BessApi, BessInfo

bess = Blueprint('bess', __name__, url_prefix='/bess')

@bess.route('/')
def index():
    return 'hallo bess'
bessapi = Api(bess)

bessapi.add_resource(BessApi, '/<string:conf>')
bessapi.add_resource(BessInfo, '/info')

