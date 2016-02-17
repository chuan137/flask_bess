from flask import Response
from flask_restful import Resource
from ...adeireader.adeireader import ADEIReader
import os, json
import copy
from operator import itemgetter

configurations = ['bess32', 'bess250', 'pvcn1000']

def open_config(conf):
    cdir = os.path.dirname(__file__)
    fname = 'config/{}.json'.format(conf)
    with open(os.path.join(cdir, fname)) as f:
        return json.load(f)

def init_adei(s):
    return ADEIReader(s.get('url'), s.get('server'), s.get('database'))

def init_group(s):
    res = {}
    for grpname, sensors in s.iteritems():
        res[grpname] = [_.get('sensor') for _ in sensors]
    return res

def ordered_sensor(conf):
    sensor_list = []
    conf = copy.deepcopy(conf)
    for c in conf:
        for grp,sns in c['sensors'].iteritems():
            for s in sns:
                s['sensor'] = grp+'.'+s['sensor']
            sensor_list.extend(sns)
    sensor_list = sorted(sensor_list, key=itemgetter('order'))
    return [_['sensor']  for _ in sensor_list]

def output_html(data, code, headers=None):
    if type(data) is list:
        data = ", ".join(data)
    resp = Response(data, mimetype='text/html', headers=headers)
    resp.status_code = code
    return resp

adei = {}
for c in configurations:
    conf = open_config(c)
    if not isinstance(conf, list): conf = [ conf ]

    _ordered = ordered_sensor(conf)
    adei[c] = dict(db=[], ordered_sensor=_ordered)

    for s in conf:
        _adei = init_adei(s)
        _group = init_group(s.get('sensors'))
        adei[c]['db'].append({'adei': _adei, 'sensor_group': _group})


class BessApi(Resource):

    def get(self, conf=None):

        # test if configuration defined
        try:
            db = adei[conf]['db']
            ordered = adei[conf]['ordered_sensor']
        except KeyError:
            confs = ""
            for i in configurations: confs += '/%s' % i
            return output_html("Wrong query: possible configurations are %s" % confs, 404)

        data = {}
        for _db in db:
            _adei = _db.get('adei')
            for grp, sns in _db.get('sensor_group').iteritems():
                q = _adei.query_data(grp, sns)
                for sns, val in q.iteritems():
                    data['.'.join([grp, sns])] = val[0]

        data_list = [data.get(s) or 'nan' for s in ordered ]
        data_list = ['%.3f'%float(f)  for f in data_list]

        return output_html(data_list, 200)
        # return data

class BessInfo(Resource):

    def get(self):
        info = {}
        info["groups"] = adeibess.query_group()
        info["sensors"] = adeibess.query_sensor()
        return info


