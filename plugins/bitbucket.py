#!/usr/bin/env python

"""
!git <command> [options] is a command line interface to bitbucket

Commands:
* `adduser`: add a user
    ex: `!git adduser -u <user>`
* `addrepo`: create a repository in a project
    ex: `!git addrepo -p <project> <reponame>`
* `addproject`: create a project
    ex: `!git addproject <project>`
"""
from __future__ import print_function
from __future__ import unicode_literals

import argparse
import re
from .devops_core import DevopsPlugin


class BitbucketPlugin(DevopsPlugin):
    """Plugin to act as a git command line interface"""

    plugin_name = 'bitbucket'
    help_message = ' `git commands` '
    help_message += '\r\n ``` !git adduser -u <user> -e <email> -d <display_name>\n !git addrepo -r <repo> -p <project> \n !git addproject -p <project> -d <description>\n !git addpermission -u <user> +rd/+w/+a <permission> -p <project> OR \n !git addpermission -u <user>  <permission> -p <project> -r <repo>``` '
    help_message+='\r\n ``` use +rd for readpermission\n use +w for writepermission \n use +a for adminpermission```'
    def git_help(self, data):
        self.outputs.append([data['channel'], self.help_message])

    def adduser(self, data, namespace):
        if namespace.user and namespace.email and namespace.desc:
            arguments = {'user': namespace.user,
                         'email': namespace.email,
                         'display_name': namespace.desc,
                         'channel': data['channel']}
            print ("Hai")
            self.ingest(b'git-adduser', arguments)
            return True
        else:
            msg = '```[user & email & display_name] options are necessary for this command```'
            msg += '\r\n `Usage:git <command> [options]` \r\n Type !git help for more info'
            self.outputs.append([data['channel'], msg])
            return False

    def addrepo(self, data, namespace):
        if namespace.project and namespace.repo:

            arguments = {'project': namespace.project, 'repo': namespace.repo,
                         'channel': data['channel']}
            self.ingest(b'git-addrepo', arguments)
            return True
        else:
            msg = '```[project & repo] options are necessary for this command```'
            msg += '\r\n `Usage:git <command> [options]` \r\n Type !git help for more info'
            self.outputs.append([data['channel'], msg])
            return False

    def addproject(self, data, namespace):

        if namespace.project and namespace.desc :

            arguments = {'project_name': namespace.project, 'description': namespace.desc,
                         'channel': data['channel']}
            self.ingest(b'git-addproject', arguments)
            return True
        else:
            msg = '```[project] options are necessary for this command```'
            msg += '\r\n `Usage:git <command> [options]` \r\n Type !git help for more info'
            self.outputs.append([data['channel'], msg])
            return False

    def addpermission(self, data, namespace):

        if namespace.user and (namespace.readpermission or namespace.writepermission or namespace.adminpermission):
            if namespace.readpermission:
                permission="r"
            elif namespace.writepermission:
                 permission="w"
            else:
                permission="a"

            if namespace.repo and namespace.project:
                #repo level permission

                arguments = {'user': namespace.user, 'permission': permission,
                             'repo': namespace.repo, 'project': namespace.project,
                             'channel': data['channel']}
                self.ingest(b'git-addpermission', arguments)
                return True

            elif namespace.project:
                # project level permission
                arguments = {'user': namespace.user, 'permission': permission,
                             'project': namespace.project, 'channel': data['channel']}
                self.ingest(b'git-addpermission', arguments)
                return True
            else:
                msg = '```[project | project & repo] options are necessary for this command```'
                msg += '\r\n `Usage:git <command> [options]` \r\n Type !git help for more info'
                self.outputs.append([data['channel'], msg])
                return False
        else:
            msg = '```[user & permission] options are necessary for this command```'
            msg += '\r\n `Usage:git <command> [options]` \r\n Type !git help for more info'
            self.outputs.append([data['channel'], msg])
            return False

    def process_message(self, data):
        print ("process message")
        if data['user'] in self.users_white_list:
            return

        class MyAction(argparse.Action):
            def __call__(self, parser, namespace, values, option_string=None):
                setattr(namespace, self.dest, ' '.join(values))



        text = data['text']
        match = re.findall(r"!git\s*(.*)", text)

        if not match :
            return

        parser = argparse.ArgumentParser(prefix_chars='-+')
        parser.add_argument('-r', '--repo')
        parser.add_argument('-u', '--user')
        parser.add_argument('-p', '--project')

        parser.add_argument('+rd','--readpermission', action='store_true')
        parser.add_argument('+w', '--writepermission', action='store_true')
        parser.add_argument('+a', '--adminpermission', action='store_true')
        parser.add_argument('-e', '--email')
        parser.add_argument('-d', '--desc', required=False,nargs='+',action=MyAction)
        parser.add_argument('command', nargs=1)

        try:
            ns = parser.parse_args(filter(None, match[0].split(' ')))


        except SystemExit:
            self.outputs.append([data['channel'],
                                 '~{0}~ Invalid format \r\n Refer the followings \r\n {1}'.format(text,
                                                                                                  self.help_message)])
            return __doc__

        command = ns.command[0]

        if command not in ['adduser', 'addrepo', 'addproject', 'addpermission', 'help'] :
            self.outputs.append([data['channel'], '`Usage:git <command> [options]` \r\n Type !git help for more info'])
            return
        else:
            try:
                if command == 'help':
                    self.git_help(data)
                else:
                    done = getattr(self, command)(data,ns)
                    if done:
                        reply = '``` *Thank You!*  \n Your command is being executed.\r\n We will let you know as soon as the execution is over```'
                        self.outputs.append([data['channel'], reply])
            except AttributeError:
                raise Exception('Command [{}] interface method is not defined'.format(command))

