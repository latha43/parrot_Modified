from __future__ import print_function
from __future__ import unicode_literals

import datetime

from .devops_core import DevopsPlugin


class HelpPlugin(DevopsPlugin):

    def process_message(self, data):
        if data['user'] in self.users_white_list:
            return

        tokens = self.token_class.tokenize_command_subcommand(data['text'])
        tokens = list(tokens)
        if len(tokens) == 0:
            msg = '```An invalid command!!!. Please type help for more useful details```'
            self.outputs.append([data['channel'], msg])

        command = tokens[0]

        if command in ['hi', 'hello', 'help', 'good']:
            if command == 'help':
                msg = """```
Hi,

We support the following commands:

!git
!svn
!kibana
!jira

Please type <command help> for more details on the sub commands
    ex: !git help
        !svn help
```
                    """
                self.outputs.append([data['channel'], msg])
            else:
                if command == 'good':
                    period = {'AM': 'Good Morning', 'PM': 'Good Afternoon'}
                    now = datetime.datetime.today().strftime('%p')
                    self.outputs.append([data['channel'], period[now]])
                else:
                    self.outputs.append([data['channel'], command])

        elif command in ['git', 'jira', 'svn', 'confluence']:
            if not data['text'].startswith('!'):
                msg = '```Please type !{} help for more {} commands```'.format(command,command)
                self.outputs.append([data['channel'], msg])

