import os
import random
import re
import requests
import string


class JiraApi(object):
    """
    APIs

    1. Create a user
        http://[JIRA_URL]/rest/api/2.0/users
    2. Create a project
        http://[JIRA_URL]/rest/api/2.0/projects

    """
    headers = {'Content-Type': 'application/json'}
    username = os.environ.get('JIRA_ADMIN_USER')
    password = os.environ.get('JIRA_ADMIN_PWD')
    base_url = os.environ.get('JIRA_URL')
    user = 'api/2/user'
    project='api/2/project'
    issue='api/2/issue'
    issue_update='api/2/issue/{issuekey}/transitions'
    status='api/2/status'

    EXISTS = 9
    SUCCESS = True
    FAILED = False


class Jira(object):
    """
    Python wrapper for JIRA REST APIs
    """
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            print (key)
            setattr(self, key, value)

    def __call__(self, **kwargs):
        method = kwargs.get('method')
        return self.request(self, method)

    @staticmethod
    def password_gen(size=18):
        return ''.join((random.choice(string.ascii_letters + string.digits) for _ in range(size)))

    @staticmethod
    def request(obj, method):
        headers = hasattr(obj, 'headers') and obj.headers or None
        params = hasattr(obj, 'params') and obj.params or None
        data = hasattr(obj, 'data') and obj.data or None
        json = hasattr(obj, 'json') and obj.json or None

        res = requests.request(method, obj.url, auth=(JiraApi.username, JiraApi.password),
                               headers=headers, params=params, data=data, json=json)
        return res

    @classmethod
    def _valid_email(cls, mail_text):
        match = re.search(r'[\w\.-]+@[\w\.-]+', mail_text)
        if match:
            return match.group(0)

    @classmethod
    def add_user(cls, name, password, display_name, email_address):
        valid_mail_id = cls._valid_email(email_address)
        if not valid_mail_id:
            msg = 'Email id [{}] is not a valid one'.format(email_address)
            return JiraApi.FAILED, msg

        user = cls.get_users(name)
        if user:
           msg = 'User [{}] already exists'.format(name)
           return JiraApi.EXISTS, msg
        mail_id=cls.get_users(valid_mail_id)

        kwargs = dict()
        kwargs['url'] = os.path.join(JiraApi.base_url, JiraApi.user)

        kwargs['headers'] = JiraApi.headers
        kwargs['json'] = {
            'name': name,
            'password': password,
            'displayName': display_name,
            'emailAddress': valid_mail_id,

        }
        instance = cls(**kwargs)
        res=instance(method='post')
        res.raise_for_status()
        msg = 'User [{}] has been successfully created'.format(name)
        return JiraApi.SUCCESS, msg

    @classmethod
    def get_users(cls, user_info=None):
        kwargs = dict()
        kwargs['url'] =  os.path.join(JiraApi.base_url, JiraApi.user)

        if user_info:
            kwargs['params'] = {'username': user_info}
        instance = cls(**kwargs)
        res = instance(method='get')
        users = res.json()

        if users:
            try:
             if users['errorMessages']:
                return None

             else:
                return users
            except:
                return users

        else:
            return None

    @classmethod
    def create_project(cls, projectname, assigneetype, projecttypekey, lead):
        print("hai")
        tc=cls.ticket_generation('TASK_manager','description','create_project','task')

        project=cls.get_all_projects(projectname)
        user=cls.get_users(lead)
        key = cls.key_gen(projectname)
        if project:
            if project:
                msg = 'Project with this projectName [{}]  already exists'.format(projectname)
            return JiraApi.EXISTS, msg

        if user:

            kwargs = dict()
            kwargs['url'] = os.path.join(JiraApi.base_url, JiraApi.project)
            kwargs['headers'] = JiraApi.headers
            kwargs['json'] = {
                    'name': projectname,
                    'key': key,
                    'assigneeType': assigneetype,
                    "projectTypeKey": projecttypekey,
                    'lead': lead,
                }
            instance = cls(**kwargs)
            res = instance(method='post')

            res.raise_for_status()
            msg = 'Project with key [{}] has been successfully created'.format(key)
            return JiraApi.SUCCESS, msg
        else:
            msg= 'Lead does not exist so add the user and try again'
            return JiraApi.SUCCESS, msg

    @classmethod
    def key_gen(cls,projectname):
        if len(projectname)<3:
            name=projectname
        else:
            name = projectname[:3].upper()

        key1 = name.join((random.choice(string.ascii_letters) for _ in range(3)))
        key = key1.upper()
        project_key=cls.get_projects(key)

        if project_key:
            key1 = key1.join((random.choice(string.ascii_letters) for _ in range(3)))
            key = key1.upper()
            return key
        else:
            return key

    @classmethod
    def get_projects(cls,key):

        kwargs = dict()
        kwargs['url'] = os.path.join(JiraApi.base_url, JiraApi.project,key)
        if key:
            instance = cls(**kwargs)
            res = instance(method='get')
            projects = res.json()
            if projects:
                try:
                    if projects['errorMessages']:
                        return None
                    else:
                        return projects
                except:
                        return projects
            else:
                return None

    @classmethod
    def get_all_projects(cls, name):

        kwargs = dict()
        kwargs['url'] = os.path.join(JiraApi.base_url, JiraApi.project)
        print(kwargs['url'])
        instance = cls(**kwargs)
        res = instance(method='get')
        projects = res.json()

        if name:
            for p in projects:
                if p['name']==name:
                    return name
        else:
            return None

    @classmethod
    def ticket_generation(cls, projectname,description,issue_name,issuetype):


        kwargs = dict()
        kwargs['url'] = os.path.join(JiraApi.base_url, JiraApi.issue)
        print
        print kwargs['url']
        kwargs['headers'] = JiraApi.headers
        kwargs['json'] = {

            "fields": {
                "project":
                    {
                        "key": "TAS",
                        "status": {

                            "name": "To Do"
                        }
                    },
                "summary": issue_name,
                "description": description,
                "issuetype": {
                    "name": "Task"
                }
            }
        }

        instance = cls(**kwargs)
        res = instance(method='post')
        print res
        res.raise_for_status()

        return True
    @classmethod
    def ticket_view(cls):

        key ="TAS-5"
        kwargs = dict()
        kwargs['url'] = os.path.join(JiraApi.base_url, JiraApi.issue,key)
        print
        print kwargs['url']
        instance = cls(**kwargs)
        res = instance(method='get')
        projects = res.json()
        print projects
        return  True







if __name__ == '__main__':

    print(Jira.create_project('deea','PROJECT_LEAD','business','devika'))

