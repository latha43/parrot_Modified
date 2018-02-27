import run_script
from redis import Redis
from rq import Queue
from utils import serialize

serialized_data = serialize.serialize()
rq_host = serialized_data[0]
rq_port = serialized_data[1]
method_mapper = serialized_data[2]
playbook_mapper = serialized_data[3]

q = Queue(connection=Redis(host = rq_host , port = rq_port))
def message_producer(self,key,value):
    method_playbook = key.split('-')
    method = method_mapper[method_playbook[0]]
    playbook = playbook_mapper[method_playbook[1]]
    args = value
    q.enqueue(run_script.__dict__[method], playbook, args['channel'], extra_arguments=args)
