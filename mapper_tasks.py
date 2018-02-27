from redis import Redis
from rq import Queue
import run_script
from serialize_module_utils import serialize_core

dict = serialize_core.serialize()
for item in dict.iteritems():
    if "RQ_HOST" in item:
        rq_host = item[1]
    if "RQ_PORT" in item:
        rq_port = item[1]
    if "MAPPER_FILE" in item:
        mapper_file = item[1]
    if "METHOD_MAPPER" in item:
        item[1][0] = {key: mapper_file for key in item[1][0]}
        method_mapper_value = item[1][0]
    if "PLAYBOOK_MAPPER" in item:
        playbook_mapper_value = item[1][0]

q = Queue(connection=Redis(host=rq_host, port=rq_port))

method_mapper = method_mapper_value

playbook_mapper = playbook_mapper_value


def message_producer(key,value):
    method_playbook = key.split('-')
    method = method_mapper[method_playbook[0]]
    playbook = playbook_mapper[method_playbook[1]]
    args = value
    q.enqueue(run_script.__dict__[method], playbook, args['channel'], extra_arguments=args)