# -*- coding: utf-8 -*-
# Copyright 2012 Dag Wieers <dag@wieers.com>
#
# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.

# Make coding more python3-ish
from __future__ import (absolute_import, division)
__metaclass__ = type
from jira import JIRA
import re
import os

from ansible.plugins.callback import CallbackBase

from slackclient import SlackClient


class CallbackModule(CallbackBase):


    """
    This Ansible callback plugin notify errors to interested parties.
    """
    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = 'notification'
    CALLBACK_NAME = 'slack'

    def __init__(self):
        super(CallbackModule, self).__init__()

        self.loop_items = []
        self.is_failed = False
        self.is_ok = False


    def v2_runner_on_failed(self, res, ignore_errors=False):

        self.loop_items.append(res)
        self.is_failed = True


    def v2_runner_on_unreachable(self, res):

        self.loop_items.append(res)
        self.is_failed = True


    def v2_runner_on_async_failed(self, res):

        self.loop_items.append(res)
        self.is_failed = True

    def v2_runner_on_ok(self, res, **kwargs):
        self.loop_items.append(res)
        self.is_ok = True

    def notify_slack(self, slack_channel):
        slack_client = SlackClient(os.environ.get('SLACK_API_TOKEN'))
        for res in self.loop_items[1:]:
            pwd_info = res._result.has_key('pwd') and res._result['pwd'] or None
            if pwd_info:
                msg = '```Your password is [{}]```'.format(pwd_info)
                print slack_client.api_call("chat.postMessage", channel=slack_channel, text=msg,username="devbotuser")

            if res._result.has_key('message'):
                msg = '`{0} : {1}`'.format(res.task_name, res._result['message'])
                print slack_client.api_call(
                    "chat.postMessage", channel= slack_channel, text=msg,
                    username="devbotuser")

    def notify_jira(self,  slack_channel):
        slack_client = SlackClient(os.environ.get('SLACK_API_TOKEN'))
        username = os.environ.get('JIRA_TICKET_USER')
        password = os.environ.get('JIRA_TICKET_PWD')
        base_url = os.environ.get('JIRA_TICKET_URL')
        project_key=os.environ.get('JIRA_PROJECT_KEY')
        options = {
            'server': base_url
        }

        Jira = JIRA(basic_auth=(username, password), options=options)
        for res in self.loop_items[1:]:

            if res._result.has_key('changed'):

                if res._result['changed'] == True:

                    message = res._result['message']
                    task = 'devbotuser: {0} requested by {1} completed'.format(res.task_name,slack_channel)

                    issue_dict = {
                        'project': project_key,
                        'summary': task,
                        'description': message,
                        'issuetype': {'name': 'Task'},
                    }

                    new_issue = Jira.create_issue(fields=issue_dict)
                    print new_issue
                    Jira.transition_issue(new_issue, '21')




