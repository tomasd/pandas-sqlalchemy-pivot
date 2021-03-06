import datetime

def unix_time(dt):
    epoch = datetime.datetime.utcfromtimestamp(0)

    if isinstance(dt, datetime.date):
        dt = datetime.datetime.combine(dt, datetime.time())

    delta = dt - epoch
    return delta.total_seconds()

def unix_time_millis(dt):
    return unix_time(dt) * 1000.0
