#!/usr/bin/env python
import sys
from redis import Redis
from rq import Connection, Worker
from utils import serialize

serialized_data = serialize.serialize()
rq_host = serialized_data[0]
rq_port = serialized_data[1]

redis = Redis(host=rq_host, port=rq_port)
with Connection(connection=redis):
    print ("workrer")
    qs = sys.argv[1:] or ['default']

    w = Worker(qs)
    w.work()
