# -*- coding: utf-8 -*-

import datetime

from cdsoss.common import timeutils

def validate(filter, value):
    return FILTER_FUNCTIONS.get(filter, lambda v: True)(value)

def sanitize_timestamp(timestamp):
    """Return a naive utc datetime object."""
    if not timestamp:
        return timestamp
    if not isinstance(timestamp, datetime.datetime):
        timestamp = timeutils.parse_isotime(timestamp)
    return timeutils.normalize_time(timestamp)


def stringify_timestamps(data):
    """Stringify any datetimes in given dict."""
    isa_timestamp = lambda v: isinstance(v, datetime.datetime)
    return dict((k, v.isoformat() if isa_timestamp(v) else v)
                for (k, v) in data.iteritems())

def validate_timestamps(timestamp):
    timestamp = sanitize_timestamp(timestamp)     
    isa_timestamp = isinstance(timestamp, datetime.datetime)
    return isa_timestamp

def validate_int_in_range(min=0, max=None):
    def _validator(v):
        try:
            if max is None:
                return min <= int(v)
            return min <= int(v) <= max
        except ValueError:
            return False
    return _validator


def validate_boolean(v):
    return v.lower() in ('none', 'true', 'false', '1', '0')


FILTER_FUNCTIONS = {'start_timestamp': validate_timestamps,
                    'end_timestamp': validate_timestamps, }
