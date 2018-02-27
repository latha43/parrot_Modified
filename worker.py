#!/usr/bin/env python
import sys
from redis import Redis
from rq import Connection, Worker
from module_utils import serialize_core

dict = serialize_core.serialize()
for item in dict.iteritems():
    if "RQ_HOST" in item:
        rq_host = item[1]
    if "RQ_PORT" in item:
        rq_port = item[1]

redis = Redis(host=rq_host, port=rq_port)

with Connection(connection=redis):
    qs = sys.argv[1:] or ['default']
    w = Worker(qs)
    w.work()
