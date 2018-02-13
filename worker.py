#!/usr/bin/env python
import sys
from redis import Redis
from rq import Connection, Worker

redis = Redis(host='10.10.114.174', port=6379)

with Connection(connection=redis):
    qs = sys.argv[1:] or ['default']

    w = Worker(qs)
    w.work()
