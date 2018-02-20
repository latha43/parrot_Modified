
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


def ingest_new(key,value):

    method_playbook = key.split('-')
    method = method_mapper[method_playbook[0]]
    playbook = playbook_mapper[method_playbook[1]]
    args = value

    q.enqueue(run_script.__dict__[method], playbook, args['channel'], extra_arguments=args)
