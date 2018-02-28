import os
import sys
from collections import namedtuple
import re
from ansible.parsing.dataloader import DataLoader
from ansible.vars import VariableManager
from ansible.inventory import Inventory
from ansible.executor.playbook_executor import PlaybookExecutor

from slackclient import SlackClient


def send_message(slack_channel, msg):
    slack_client = SlackClient(os.environ.get('SLACK_API_TOKEN'))
    print slack_client.api_call(
        "chat.postMessage", channel=slack_channel, text=msg,
        username="devbotuser")


def run_script(playbook_path,channel,inventory_sources=None,extra_arguments={}):
    Options = namedtuple('Options',
                ['listtags', 'listtasks', 'listhosts', 'syntax', 'connection', 'module_path', 'forks',
                 'remote_user', 'private_key_file', 'ssh_common_args', 'ssh_extra_args', 'sftp_extra_args',
                 'scp_extra_args', 'become', 'become_method', 'become_user', 'verbosity', 'check', 'diff'])
    options = Options(listtags=False, listtasks=False, listhosts=False, syntax=False, connection='ssh',
                      module_path=None, forks=100, remote_user='u54863', private_key_file=None,
                      ssh_common_args=None, ssh_extra_args=None, sftp_extra_args=None, scp_extra_args=None,
                      become=False, become_method=None, become_user=None, verbosity=True, check=False, diff=False)

    if not os.path.exists(playbook_path):
        print '[INFO] The playbook does not exist'
        sys.exit()

    loader = DataLoader()
    variable_manager = VariableManager()
    inventory = Inventory(loader, variable_manager)
    variable_manager.extra_vars = extra_arguments  # This can accomodate various other command line arguments.`

    passwords = {}

    pbex = PlaybookExecutor(playbooks=[playbook_path], inventory=inventory,
                            variable_manager=variable_manager, loader=loader,
                            options=options, passwords=passwords)
    pbex.run()
    stats = pbex._tqm._stats
    hosts = sorted(stats.processed.keys())
    run_success = True
    for h in hosts:
        t = stats.summarize(h)
        if t['unreachable'] > 0 or t['failures'] > 0:
            run_success = False
            send_message(channel, '```{}```'.format(str(t)))


    pbex._tqm.send_callback('notify_jira',channel)
    pbex._tqm.send_callback('notify_slack', channel)

    if run_success:
        send_message(channel, '```Execution is completed. Please check the result```')

if __name__ == '__main__':
    arguments = {
            'project_name': 'test1_project',
            'description': 'This is a test project'
            }
    run_script(sys.argv[1], sys.argv[2], extra_arguments=arguments)