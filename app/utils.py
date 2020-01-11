from datetime import datetime


def dateformats():
    """ Possible date formats. Both of them are used by the Camara dos Deputados data API. """
    return ['%Y-%m-%d', '%d/%m/%Y']


def str2date(string):
    """Parse a string into a datetime object."""
    for fmt in dateformats():
        try:
            return datetime.strptime(string, fmt)
        except ValueError:
            pass
    raise ValueError("'%s' is not a recognized date/time" % string)


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