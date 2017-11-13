import signal
import datetime

cache = ""
alarmInterval = 20


def log(content):
    global cache
    cache += str(datetime.datetime.now().time())
    cache += ": "
    cache += str(content)
    cache += "\n"


def reset():
    signal.alarm(alarmInterval)
    global cache
    cache = ""


def init():
    signal.signal(signal.SIGALRM, alarmHandler)


def alarmHandler():
    print(cache)
    raise Exception("Timeout")
