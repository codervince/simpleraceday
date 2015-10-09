from datetime import datetime
import re

def cleanstring(s):
    pattern = re.compile(r'\s+')
    return re.sub(pattern, u' ',s).sub(u'-', u'')

def try_float(value):
    try:
        return float(value)
    except:
        return 0.0

def try_int(value):
    try:
        return int(value)
    except:
        return 0