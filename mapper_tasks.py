from redis import Redis
from rq import Queue
import run_script
import yaml

with open("rtmbot.conf") as stream:
        dict=yaml.load(stream)
        for key, value in dict.iteritems():
            if "RQ_HOST" in key:
                RQ_HOST=value
            if "RQ_PORT" in key:
                RQ_PORT=value
            if "METHOD_MAPPER" in key:
                METHOD_MAPPER=value[0]
            if "PLAYBOOK_MAPPER" in key:
                PLAYBOOK_MAPPER=value[0]

q = Queue(connection=Redis(host=RQ_HOST, port=RQ_PORT))

method_mapper = METHOD_MAPPER

playbook_mapper = PLAYBOOK_MAPPER


def message_producer(key,value):
    method_playbook = key.split('-')
    method = method_mapper[method_playbook[0]]
    playbook = playbook_mapper[method_playbook[1]]
    args = value
    q.enqueue(run_script.__dict__[method],playbook,args['channel'],extra_arguments=args)
