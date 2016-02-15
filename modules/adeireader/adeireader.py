#!/usr/bin/env python
# -*- coding: utf-8 -*-
import numpy
from adeihelper import query_csv, query_xml, adei_timestamp, print_exc

DEBUG = 0


class AdeiError(Exception):
    'not implemented'
    def __init__(self, message):
        super(AdeiError, self).__init__(message)


class ADEIReader(object):

    def __init__(self, host, server, db):
        self.host = host + '/services/'
        self.server = server
        self.db = db

        self._groups = []
        self._sensors = {}
        self.update_group_list()

    def qurl(self, qtype, **kwargs):
        url = self.host

        if qtype == 'get':
            url = url + 'getdata.php?'
        elif qtype == 'group':
            url = url + 'list.php?target=groups'
        elif qtype == 'sensor':
            url = url + 'list.php?target=items'

        kwargs['db_server'] = self.server
        kwargs['db_name'] = self.db
        kwargs['window'] = kwargs.get('window') or '-1'
        kwargs['resample'] = kwargs.get('resample') or '0'

        for k, v in kwargs.iteritems():
            url += '&' + k + '=' + str(v)

        if DEBUG:
            print url
        return url

    def update_group_list(self):
        url = self.qurl('group')
        self._groups = query_xml(url)

    def update_sensor_list(self, groupname, force=False):
        url = self.qurl('sensor', db_group=groupname)
        self._sensors[groupname] = { v['name']:v['value'] for v in  query_xml(url) }

    def query_data(self, group, sensors, **kwargs):
        '''
        Fetch data from ADEI server
        '''
        if not isinstance(sensors, list):
            sensors = [ sensors ]

        if group not in self._sensors:
            self.update_sensor_list(group)

        for s in sensors:
            if s not in self._sensors[group]:
                raise AdeiError('sensor name `%s` not found in group %s' % (s, group))

        masks = map(self._sensors.get(group).get, sensors)
        masks = map(int, masks)
        masks = sorted(masks)

        data = self._query(group, *masks, **kwargs)
        data = self._serialize(data)

        return data

    def _serialize(self, data):
        res = dict()
        for i in range(len(data)):
            if data[i][0] == 'Date/Time':
                res['timestamp'] = map(adei_timestamp, data[i][1:])
            else:
                res[data[i][0]] = list(data[i][1:])
        return res

    def _query(self, group, *masks, **kwargs):
        masks = ','.join(map(str, masks))
        url = self.qurl('get', db_group=group, db_mask=masks, **kwargs)
        return query_csv(url)

    @property
    def sensors(self):
#        if not self._sensors:
#            print 'retrieve sensor list'
#            self._sensors = self.get_sensor_list()
        return self._sensors

    @property
    def groups(self):
        return self._groups

