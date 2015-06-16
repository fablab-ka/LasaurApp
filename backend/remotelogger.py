""" remotelogger.py

A Wrapper around the influxdb client, if influxdb is not available it will fallback to stdout.

"""
from __future__ import print_function
from datetime import datetime

INFLUXDB_ENABLED = False
try:
    from influxdb import InfluxDBClient
    INFLUXDB_ENABLED = True
except ImportError:
    print("[TimeMonitor] No InfluxDB Installed, if you want remote logging, please install 'pip install influxdb'")


class RemoteLogger(object):
    def __init__(self, channel, config):
        self.channel = channel

        if INFLUXDB_ENABLED:
            self.client = InfluxDBClient(config.influx_host, config.influx_port, config.influx_user, config.influx_pw, config.influx_db)

    def log(self, *args):
        message = str.join(" ", [str(elem) for elem in args])

        if INFLUXDB_ENABLED:
            self.client.write_points([{
                "name": "lasersaur",
                "level": "log",
                "timestamp": datetime.now(),
                "channel": self.channel,
                "message": message
            }])
        else:
            print("[LOG] " + message)

    def info(self, *args):
        message = str.join(" ", [str(elem) for elem in args])

        if INFLUXDB_ENABLED:
            self.client.write_points([{
                "name": "lasersaur",
                "level": "info",
                "timestamp": datetime.now(),
                "channel": self.channel,
                "message": message
            }])
        else:
            print("[INFO] " + message)