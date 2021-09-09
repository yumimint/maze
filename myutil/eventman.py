import collections
import weakref

wsdic = collections.defaultdict(weakref.WeakSet)


def broadcast(channel, *args, **kwargs):
    if channel in wsdic:
        for func in wsdic[channel]:
            func(*args, **kwargs)


def addlistener(channel, func):
    wsdic[channel].add(func)
    return func


def listener(channel):
    def decorator(func):
        wsdic[channel].add(func)
        return func
    return decorator
