import json

from kafka import KafkaConsumer
from redis import Redis
from rq import Queue

import run_script

q = Queue(connection=Redis(host='10.10.114.174', port=6379))

method_mapper = {
    'git': 'run_script',
    'jira': 'run_script'
    }

playbook_mapper = {
    'adduser': 'ansible/bb_user.yml',
    'addproject': 'ansible/bb_project.yml',
    'addrepo': 'ansible/bb_repo.yml',
    'addpermission': 'ansible/bb_permission.yml',
    'newuser': 'ansible/jira_user.yml',
    'newproject': 'ansible/jira_project.yml'
    }

consumer = KafkaConsumer('chat-bot-topic-devops', bootstrap_servers='10.10.114.174:9092',
                        value_deserializer=lambda m: json.loads(m))
for msg in consumer:
    print(msg)
    method_playbook = msg.key.split('-')

    method = method_mapper[method_playbook[0]]
    playbook = playbook_mapper[method_playbook[1]]
    args = msg.value
    q.enqueue(run_script.__dict__[method], playbook, args['channel'], extra_arguments=args)
