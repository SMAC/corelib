def timedelta(timedelta, sep=' '):
    if not timedelta or isinstance(timedelta, basestring):
        return timedelta
    
    days = timedelta.days
    hours = timedelta.seconds // 3600
    minutes = (timedelta.seconds - hours * 3600) // 60
    seconds = timedelta.seconds - hours * 3600 - minutes * 60
    
    times = [days, hours, minutes, seconds]
    rep = ['{0}d'.format(days), '{0}h'.format(hours), '{0}m'.format(minutes), '{0}s'.format(seconds)]
    
    while not times[0] and len(times) > 1:
        times.pop(0)
        rep.pop(0)
    
    if len(rep) == 1:
        return '{0} seconds'.format(seconds)
        
    return sep.join(rep[0:2])

def size(num):
    for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if num < 1024.0:
            return "%3.1f %s" % (num, x)
        num /= 1024.0