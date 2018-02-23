from redis import Redis
from rq import Queue
import run_script
import yaml

with open("rtmbot.conf","r") as file:
    dic=yaml.load(file)
    for key,value in dic.iteritems():
        if key=="HOST":
            HOST=value
        if key=="PORT":
            PORT=value
        if key=="METHOD_MAPPER":
            method_mapper=value[0]
        if key=="PLAYBOOK_MAPPER":
            playbook_mapper=value[0]


q = Queue(connection=Redis(host= HOST , port=PORT))

def message_producer(self,key,value):
    method_playbook = key.split('-')
    method = method_mapper[method_playbook[0]]
    playbook = playbook_mapper[method_playbook[1]]
    args = value
    q.enqueue(run_script.__dict__[method], playbook, args['channel'], extra_arguments=args)
