import re
import sys
import datetime
import calendar
import colorstring
import base64
import csv
import json
import xml.etree.ElementTree as ET
import traceback
import urllib2 as urllib
import numpy as np

ADEI_Time_Format = '%d-%b-%y %H:%M:%S.%f'

def xmlparser(handler):
    tree = ET.parse(handler)
    result = []
    for child in tree.getroot():
        result.append(child.attrib)
    return result

def csvparser(handler):
    rows = csv.reader(handler, skipinitialspace=True)
    fields = rows.next()
    data = [row for row in rows if row]
    return zip(fields, *data)

def print_exc():
    exctype, value, tb  = sys.exc_info()
    filename, linenumber, functionname, text =  traceback.extract_tb(tb, 1)[0]
    sys.stderr.write("[Error] Unexpected exception\n")
    sys.stderr.write("            type: %s\n" % exctype)
    sys.stderr.write("         message: %s\n" % colorstring.ERROR(value.message))
    sys.stderr.write("        function: %s\n" % colorstring.ERROR(functionname))
    sys.stderr.write("            text: %s\n" % text)
    sys.stderr.write("            file: %s: %s\n" % (filename, linenumber))

def adei_timestamp(adeitimestr):
    timestamp = datetime.datetime.strptime(adeitimestr, ADEI_Time_Format)
    timestamp = calendar.timegm(timestamp.timetuple())
    return timestamp

def utc_timestamp(year, month, day):
    d = datetime.datetime(year, month, day)
    timestamp = calendar.timegm(d.timetuple())
    return timestamp

def start_of_day(timestamp, tz='UTC'):
    hour, min, sec = datetime.datetime.utcfromtimestamp(timestamp).strftime("%H %M %S").split()
    hour, min, sec = map(int, [hour, min, sec])
    return timestamp - (hour*3600 + min*60 + sec)

def query_csv(url, username=None, password=None):
    request = urllib.Request(url)
    if username and password:
        base64string = base64.encodestring('%s:%s' % ( username, password ) )
        request.add_header("Authorization", "Basic %s" % base64string)
    fp = urllib.urlopen(request)
    resp = csvparser(fp)
    return resp

def query_xml(url, username=None, password=None):
    request = urllib.Request(url)
    if username and password:
        base64string = base64.encodestring('%s:%s' % ( username, password ) )
        request.add_header("Authorization", "Basic %s" % base64string)
    fp = urllib.urlopen(request)
    return xmlparser(fp)


class NumpyEncoder(json.JSONEncoder):

    def default(self, obj):
        """If input object is an ndarray it will be converted into a dict 
        holding dtype, shape and the data, base64 encoded.
        """
        if isinstance(obj, np.ndarray):
            if obj.flags['C_CONTIGUOUS']:
                obj_data = obj.data
            else:
                cont_obj = np.ascontiguousarray(obj)
                assert(cont_obj.flags['C_CONTIGUOUS'])
                obj_data = cont_obj.data
            data_b64 = base64.b64encode(obj_data)
            return dict(__ndarray__=data_b64,
                        dtype=str(obj.dtype),
                        shape=obj.shape)
        # Let the base class default method raise the TypeError
        return json.JSONEncoder(self, obj)

def json_numpy_obj_hook(dct):
    """Decodes a previously encoded numpy ndarray with proper shape and dtype.

    :param dct: (dict) json encoded ndarray
    :return: (ndarray) if input was an encoded ndarray
    """
    if isinstance(dct, dict) and '__ndarray__' in dct:
        data = base64.b64decode(dct['__ndarray__'])
        return np.frombuffer(data, dct['dtype']).reshape(dct['shape'])
    return dct
#
# expected = np.arange(100, dtype=np.float)
# dumped = json.dumps(expected, cls=NumpyEncoder)
# result = json.loads(dumped, object_hook=json_numpy_obj_hook)
#
#
# # None of the following assertions will be broken.
# assert result.dtype == expected.dtype, "Wrong Type"
# assert result.shape == expected.shape, "Wrong Shape"
# assert np.allclose(expected, result), "Wrong Values"
