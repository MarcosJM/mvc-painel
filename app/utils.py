from datetime import datetime
import math
import json
import seaborn as sns
import random
from app import dbConn


LEGISLATURES = [53, 54, 55, 56]
YEARS = [2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019]

with open('app/party_colors.json') as f:
    PARTY_COLORS = json.load(f)


def getLegislativeBody(body_name):
    """  """
    try:
        body = list(dbConn.build_collection('orgao').find({"tipoOrgao": body_name}, {'_id': 0, 'sigla': 1}))
        if len(body) > 0:
            body_initials = [item['sigla'] for item in body]
            return body_initials
        else:
            return None
    except Exception as e:
        print(e)


def format_number(number, units=['', 'K', 'M', 'G', 'T', 'P']):
    """ function for formatting big numbers """
    k = 1000.0
    magnitude = int(math.log10(number) // 3)
    return '%.2f%s' % (number / k**magnitude, units[magnitude])


def color_party(party_initials):
    """ get a party color """
    try:
        initials = party_initials.lower()
        auxiliary_pallete = sns.color_palette("cubehelix", 10).as_hex()  # when a party does not have a color

        symbols = "!@#$*-/"
        for char in symbols:
            initials = initials.replace(char, "")  # removing some symbols

        if initials in PARTY_COLORS.keys():
            color = PARTY_COLORS[initials]
            return color
        else:
            return random.choice(auxiliary_pallete)
    except Exception as e:
        print(e)


def dateformats():
    """ Possible date formats. Both of them are used by the Camara dos Deputados data API. """
    return ['%Y-%m-%d', '%Y-%m-%dT%H:%M:%S', '%d/%m/%Y']


def str2date(string):
    """Parse a string into a datetime object."""
    for fmt in dateformats():
        try:
            date = datetime.strptime(string, fmt)
            # making sure ignoring time
            date = date.replace(year=date.year, month=date.month, day=date.day, hour=0, minute=0)
            return date
        except ValueError:
            pass
    raise ValueError("'%s' is not a recognized date/time" % string)


def date2timestamp(date):
    try:
        if type(date) == str:
            datetime_obj = str2date(date)
            return datetime_obj.timestamp()

        elif type(date) == datetime:
            return date.timestamp()
    except Exception as e:
        print(e)


def get_records_by_intervals(records, dates, data_key):
    """ Given a records with date (accessed by data_key) and dates, recover the events within the dates ranges. """
    if len(dates) == 1:  # if it's only one date
        date_start = str2date(dates[0][0])
        date_finish = str2date(dates[0][1])
        result = [item for item in records if date_start <= str2date(item[data_key]) <= date_finish]

    elif len(dates) > 1:  # more than one date to compare
        result = []
        for date in dates:
            date_start = str2date(date[0])
            date_finish = str2date(date[1])
            result += [item for item in records if date_start <= str2date(item[data_key])
                       <= date_finish]
    return result
