#!/usr/bin/env python

"""
!jira <command> [options] is a command line interface to jira

Commands:
* `adduser`: add a user
    ex: `!jira adduser -u <user>`
* `addproject`: create a project
    ex: `!git addproject <project>`
"""
from __future__ import print_function
from __future__ import unicode_literals

import argparse
import re
from .devops_core import DevopsPlugin

class JiraPlugin(DevopsPlugin):
    """Plugin to act as a git command line interface"""

    plugin_name = 'jira'
    help_message = ' `jira commands` '
    help_message += '\r\n```!jira newuser -u <user> -e <email> -d <display_name>\n\n!jira newproject -p <project name> -l <lead>\tOR\n!jira newproject -p <project name> -at <ASSIGNE_TYPE> -pk <project type key> -l <lead>\n\n\t\t***ASSIGNEE TYPE should be PROJECT_LEAD or UNASSIGNED***\n\t\t***project type key should be business***``` '

    def jira_help(self, data):
        self.outputs.append([data['channel'], self.help_message])

    def newuser(self, data, namespace):

        if namespace.user and namespace.email and namespace.desc:
            arguments = {'name': namespace.user,
                         'email_address': namespace.email,
                         'display_name': namespace.desc,
                         'channel':data['channel']}
            self.ingest(b'jira-newuser', arguments)
            return True

        else:
            msg = '```[user & email & display_name] options are necessary for this command```'
            msg += '\r\n `Usage:jira <command> [options]` \r\n Type !jira help for more info'
            self.outputs.append([data['channel'], msg])
        return False

    def check(self,assignee, proj_type):
        Flag = True
        msg = ""
        if assignee not in (['UNASSIGNED', 'PROJECT_LEAD']):
            Flag = False
            msg = "assignee Type should be UNASSIGNED or PROJECT_LEAD"
        if not proj_type == 'business':
            Flag = False
            msg += "\nproject type key should be business"
        return Flag,msg


    def newproject(self, data, namespace):
        flag,msg=self.check(namespace.assignee,namespace.typekey)
        if namespace.project and namespace.lead:
                if flag:
                        arguments = {'projectName': namespace.project,'assigneeType':namespace.assignee,'projectTypeKey':namespace.typekey,'lead':namespace.lead,
                         'channel': data['channel']}
                        self.ingest(b'jira-newproject', arguments)
                        return True
                else:
                    self.outputs.append([data['channel'],msg])
                    return False

        else:
            msg = '```[project] options are necessary for this command```'
            msg += '\r\n `Usage:jira <command> [options]` \r\n Type !jira help for more info'
            self.outputs.append([data['channel'], msg])
            return False

    def process_message(self, data):
        if data['user'] in self.users_white_list:
            return

        class MyAction(argparse.Action):
            def __call__(self, parser, namespace, values, option_string=None):
                setattr(namespace, self.dest, ' '.join(values))

        text = data['text']
        match = re.findall(r"!jira\s*(.*)", text)

        if not match :
            return

        parser = argparse.ArgumentParser()
        parser.add_argument('-u', '--user')
        parser.add_argument('-p', '--project')
        parser.add_argument('-at', '--assignee', required=False,default='UNASSIGNED')
        parser.add_argument('-l', '--lead')
        parser.add_argument('-pk', '---typekey', required=False,default='business')
        parser.add_argument('-e', '--email')
        parser.add_argument('-d', '--desc', required=False,nargs='+',action=MyAction)
        parser.add_argument('command', nargs=1)

        try:
            ns = parser.parse_args(filter(None, match[0].split(' ')))
            print (ns)
        except SystemExit:
            self.outputs.append([data['channel'],
                                 '~{0}~ Invalid format \r\n Refer the followings \r\n {1}'.format(text,
                                                                                                  self.help_message)])
            return __doc__

        command = ns.command[0]

        if command not in (['newuser','newproject', 'help']) :
            self.outputs.append([data['channel'], '`Usage:jira <command> [options]` \r\n Type !jira help for more info'])
            return
        else:
            try:
                if command == 'help':
                    self.jira_help(data)
                else:
                    done = getattr(self, command)(data,ns)
                    if done:
                        reply = '``` *Thank You!*  \n Your command is being executed.' \
                                                    '\r\n We will let you know as soon as the execution is over```'
                        self.outputs.append([data['channel'], reply])
            except AttributeError:
                raise Exception('Command [{}] interface method is not defined'.format(command))




