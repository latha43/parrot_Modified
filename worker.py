#!/usr/bin/env python
import sys
from redis import Redis
from rq import Connection, Worker
import yaml

with open("rtmbot.conf","r") as file:
    dic=yaml.load(file)
    for key,value in dic.iteritems():
        if key=="HOST":
            HOST=value
        if key=="PORT":
            PORT=value
redis = Redis(host=HOST, port=PORT)

with Connection(connection=redis):
    print ("workrer")
    qs = sys.argv[1:] or ['default']

    w = Worker(qs)
    w.work()
