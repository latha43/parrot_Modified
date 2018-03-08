#!/usr/bin/env python
import sys
from redis import Redis
from rq import Connection, Worker
from utils import serializer

redis = Redis(host = serializer.rq_host, port = serializer.rq_port)

with Connection(connection=redis):
    qs = sys.argv[1:] or ['default']
    w = Worker(qs)
    w.work()
