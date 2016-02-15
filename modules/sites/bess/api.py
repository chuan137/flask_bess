from flask import Response
from flask_restful import Resource
from ...adeireader.adeireader import ADEIReader
import os, json
from operator import itemgetter

configurations = ['bess32', 'bess250', 'pvcn1000']

def open_config(conf):
    cdir = os.path.dirname(__file__)
    fname = 'config/{}.json'.format(conf)
    with open(os.path.join(cdir, fname)) as f:
        return json.load(f)

def init_adei(conf):
    conf = open_config(conf)
    host, server, db = conf.get('url'), conf.get('server'), conf.get('database')
    return ADEIReader(host, server, db)

def ordered_sensor_list(conf):
    conf = open_config(conf)
    sensors = conf.get('sensors')
    for grp, sns in sensors.iteritems():
        for _ in sns:
            _['sensor'] = '{}.{}'.format(grp, _['sensor'])
    sensors = [_ for grp,sns in sensors.iteritems() for _ in sns]
    return sorted(sensors, key=itemgetter('order'))

def sensor_list(conf):
    conf = open_config(conf)
    return {k:[_.get('sensor') for _ in v] for k,v in conf.get('sensors').iteritems()}

def output_html(data, code, headers=None):
    if type(data) is list:
        data = " ".join(data)
    resp = Response(data, mimetype='text/html', headers=headers)
    resp.status_code = code
    return resp


adeireader_obj = {s : init_adei(s) for s in configurations}
sensors = {s: sensor_list(s)  for s in configurations}
sensors_ordered = {s: ordered_sensor_list(s) for s in configurations}


if 0:
    _adei = adeireader_obj['bess250']
    _g = _adei.query_group('allgemein_500')
    print map(_g.get, ['e_from_batt_act'])
    print _adei.query_data('allgemein_500', ['e_from_batt_act'] )


class BessApi(Resource):

    def get(self, conf=None):

        # test if configuration defined
        try:
            adei = adeireader_obj[conf]
            sns = sensors[conf]
            ordered = sensors_ordered[conf]
        except KeyError:
            confs = ""
            for i in configurations: confs += '/%s' % i
            return output_html("Wrong query: possible configurations are %s" % confs, 404)

        data = {}
        for grp, sns_list in sns.iteritems():
            q = adei.query_data(grp, sns_list)
            for sns, val in q.iteritems():
                data['.'.join([grp, sns])] = val[0]

        data_list = []
        for s in ordered:
            r = data.get(s['sensor']) or 'nan'
            data_list.append(r)
        data_list = ['%.3f,'%float(f)  for f in data_list]

        # return output_html(data_list, 200)
        return data

class BessInfo(Resource):

    def get(self):
        info = {}
        info["groups"] = adeibess.query_group()
        info["sensors"] = adeibess.query_sensor()
        return info


