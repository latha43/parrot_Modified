#!/usr/bin/env python
import sys
from redis import Redis
from rq import Connection, Worker
import yaml

with open("rtmbot.conf") as stream:
    dict = yaml.load(stream)
    for key, value in dict.iteritems():
        if "RQ_HOST" in key:
            RQ_HOST = value
        if "RQ_PORT" in key:
            RQ_PORT = value
redis = Redis(host=RQ_HOST, port=RQ_PORT)

with Connection(connection=redis):
    qs = sys.argv[1:] or ['default']

    w = Worker(qs)
    w.work()
