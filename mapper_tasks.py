from redis import Redis
from rq import Queue
import run_script
from utils import serializer

q = Queue(connection=Redis(host = serializer.rq_host, port = serializer.rq_port))

method_mapper = serializer.method_mapper_value

playbook_mapper = serializer.playbook_mapper_value

def message_producer(key,value):
    method_playbook = key.split('-')
    method = method_mapper[method_playbook[0]]
    playbook = playbook_mapper[method_playbook[1]]
    args = value

    q.enqueue(run_script.__dict__[method], playbook, args['channel'], extra_arguments=args)

