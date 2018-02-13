import os
import random
import re
import requests
import string


class BBApi(object):
    """
    APIs
    1. Create a new project
    http://[BITBUCKET_URL]/rest/api/1.0/projects

    2. Create a new repo in existing project
    http://[BITBUCKET_URL]/rest/api/1.0/projects/{projectKey}/repos

    3. Create a user
    http://[BITBUCKET_URL]/rest/api/1.0/admin/users

    4. Grant permissions to a user in projects
    http://[BITBUCKET_URL]/rest/api/1.0/projects/{projectKey}/permissions/users

    5. Grant permissions to a user in a specific repo of a project
    http://[BITBUCKET_URL]/rest/api/1.0/projects/{projectKey}/repos/{repositorySlug}/permissions/users

    6. Add new ssh keys
    http://[BITBUCKET_URL]/rest/ssh/1.0/keys

    7. Fork a new repo from existing repo
    http://git.devops.apmoller.net/rest/api/1.0/projects/{projectKey}/repos/{repositorySlug}
    """
    headers = {'Content-Type': 'application/json'}
    username = os.environ.get('BITBUCKET_ADMIN_USER')
    password = os.environ.get('BITBUCKET_ADMIN_PWD')
    base_url = os.environ.get('BITBUCKET_URL')
    project = 'api/1.0/projects'
    repo = 'api/1.0/projects/{project_key}/repos'
    fork_repo = 'api/1.0/projects/{project_key}/repos/{repository_slug}'
    user = 'api/1.0/admin/users'
    project_permission = 'api/1.0/projects/{project_key}/permissions/users'
    repo_permission = 'api/1.0/projects/{project_key}/repos/{repo_slug}/permissions/users'
    ssh = 'ssh/1.0/keys'

    # project permissions
    project_read = 'PROJECT_READ'
    project_write = 'PROJECT_WRITE'
    project_admin = 'PROJECT_ADMIN'

    # repo permissions
    repo_read = 'REPO_READ'
    repo_write = 'REPO_WRITE'
    repo_admin = 'REPO_ADMIN'

    EXISTS = 9
    SUCCESS = True
    FAILED = False


class BitBucket(object):
    """
    Python wrapper for bitbucket REST APIs
    """
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __call__(self, **kwargs):
        method = kwargs.get('method')
        return self.request(self, method)

    @classmethod
    def is_project_existing(cls, name=None, key=None):
        res_json = cls.get_projects(name).json()
        projects = res_json.get('values')
        exists = False
        if projects:
            for p in projects:
                if key:
                    if p['key'].lower() == key.lower():
                        exists = p
                        break
                if name:
                    if p['name'].lower() == name.lower():
                        exists = p
                        break
        return exists

    @classmethod
    def add_project(cls, name, description, avatar=None):
        key = name.replace(' ', '').upper()
        p = cls.is_project_existing(name=name)
        if p:
            msg = 'Project [{}] already exists'.format(p['key'])
            return BBApi.EXISTS, msg

        payload = {'key': key,
                   'name': name,
                   'description': description,
                   'avatar': avatar}
        url = os.path.join(BBApi.base_url, BBApi.project)
        instance = cls(json=payload, url=url)
        instance(method='post')
        msg = 'Project [{}] has been created'.format(name)
        return BBApi.SUCCESS, msg

    @classmethod
    def get_projects(cls, name=None):
        kwargs = dict()
        kwargs['url'] = os.path.join(BBApi.base_url, BBApi.project)
        if name:
            kwargs['params'] = {'name': name}
        instance = cls(**kwargs)
        res = instance(method='get')
        return res

    @staticmethod
    def password_gen(size=18):
        return ''.join((random.choice(string.ascii_letters + string.digits) for _ in range(size)))

    @staticmethod
    def request(obj, method):
        headers = hasattr(obj, 'headers') and obj.headers or None
        params = hasattr(obj, 'params') and obj.params or None
        data = hasattr(obj, 'data') and obj.data or None
        json = hasattr(obj, 'json') and obj.json or None

        res = requests.request(method, obj.url, auth=(BBApi.username, BBApi.password),
                               headers=headers, params=params, data=data, json=json)
        res.raise_for_status()
        return res

    @classmethod
    def add_repo(cls, project_key, repo_name):
        p = cls.is_project_existing(key=project_key)
        if not p:
            msg = 'Project [{}] doesnt exists'.format(project_key)
            return BBApi.FAILED, msg

        res_json = cls.get_repositories(project_key).json()
        repositories = res_json.get('values')
        if repositories:
            for r in repositories:
                if r['slug'].lower() == repo_name.lower():
                    msg = 'Repository [{}] already exists'.format(repo_name)
                    return BBApi.EXISTS, msg

        kwargs = dict()
        kwargs['url'] = os.path.join(BBApi.base_url, BBApi.repo.format(project_key=project_key))
        kwargs['params'] = {'projectKey': project_key}
        kwargs['json'] = {
                'name': repo_name,
                'scmId': 'git',
                'forkable': True
                }
        instance = cls(**kwargs)
        instance(method='post')
        msg = 'Repository [{}] has been succesfully created'.format(repo_name)
        return BBApi.SUCCESS, msg

    @classmethod
    def is_repo_exists(cls, project_key, repo_slug):
        exists = False
        p = cls.is_project_existing(key=project_key)
        if p:
            res_json = cls.get_repositories(project_key).json()
            repositories = res_json.get('values')
            if repositories:
                for r in repositories:
                    if r['slug'].lower() == repo_slug.lower():
                        exists = True
                        return exists

        return exists

    @classmethod
    def get_repositories(cls, project_key):
        kwargs = dict()
        kwargs['url'] = os.path.join(BBApi.base_url, BBApi.repo.format(project_key=project_key))
        kwargs['params'] = {'projectKey': project_key}
        instance = cls(**kwargs)
        res = instance(method='get')
        return res

    @classmethod
    def _valid_email(cls, mail_text):
        match = re.search(r'[\w\.-]+@[\w\.-]+', mail_text)
        if match:
            return match.group(0)

    @classmethod
    def add_user(cls, name, password, display_name, email_address, add_to_default_group=True):
        valid_mail_id = cls._valid_email(email_address)
        if not valid_mail_id:
            msg = 'Email id [{}] is not a valid one'.format(email_address)
            return BBApi.FAILED, msg

        user = cls.get_users(valid_mail_id)
        if user:
            msg = 'User [{}] already exists'.format(name)
            return BBApi.EXISTS, msg

        kwargs = dict()
        kwargs['url'] = os.path.join(BBApi.base_url, BBApi.user)
        kwargs['headers'] = BBApi.headers
        kwargs['params'] = {
            'name': name,
            'password': password,
            'displayName': display_name,
            'emailAddress': valid_mail_id,
            'addToDefaultGroup': add_to_default_group,
            'notify': False
        }
        instance = cls(**kwargs)
        instance(method='post')
        msg = 'User [{}] has been successfully created'.format(name)
        return BBApi.SUCCESS, msg

    @classmethod
    def delete_user(cls, name):
        user = cls.get_users(name)
        if user:
            kwargs = dict()
            kwargs['url'] = os.path.join(BBApi.base_url, BBApi.user)
            kwargs['params'] = {
                'name': name
            }
            instance = cls(**kwargs)
            res = instance(method='delete')
            return res

    @classmethod
    def get_users(cls, user_info=None):
        kwargs = dict()
        kwargs['url'] = os.path.join(BBApi.base_url, BBApi.user)
        if user_info:
            kwargs['params'] = {'filter': user_info}
        instance = cls(**kwargs)
        res = instance(method='get')
        users = res.json()['values']
        if user_info:
            for user in users:
                for info in user.values():
                    if info == user_info:
                        return user
            else:
                return None
        return users

    @classmethod
    def grant_project_permission(cls, project_key, user_name, permission=BBApi.project_read):
        if not cls.get_users(user_name):
            msg = 'User [{}] doesnt exists'.format(user_name)
            return BBApi.FAILED, msg

        p = cls.is_project_existing(key=project_key)
        if not p:
            msg = 'Project [{}] doesnt exists'.format(project_key)
            return BBApi.FAILED, msg

        kwargs = dict()
        kwargs['url'] = os.path.join(BBApi.base_url, BBApi.project_permission.format(project_key=project_key))
        kwargs['headers'] = BBApi.headers
        kwargs['params'] = {
            'name': user_name,
            'permission': permission
        }
        instance = cls(**kwargs)
        instance(method='put')
        msg = 'Permission of [{0}] in [{1}] has been changed to [{2}]'.format(user_name, project_key, permission)
        return BBApi.SUCCESS, msg

    @classmethod
    def grant_repo_permission(cls, project_key, repo_slug, user_name, permission=BBApi.repo_read):
        if not cls.get_users(user_name):
            msg = 'User [{}] doesnt exists'.format(user_name)
            return BBApi.FAILED, msg

        p = cls.is_project_existing(key=project_key)
        if not p:
            msg = 'Project [{}] doesnt exists'.format(project_key)
            return BBApi.FAILED, msg

        r = cls.is_repo_exists(project_key, repo_slug)
        if not r:
            msg = 'Repo [{}] doesnt exists'.format(repo_slug)
            return BBApi.FAILED, msg

        kwargs = dict()
        kwargs['url'] = os.path.join(BBApi.base_url, BBApi.repo_permission.format(project_key=project_key,
                                                                                  repo_slug=repo_slug))
        kwargs['headers'] = BBApi.headers
        kwargs['params'] = {
            'name': user_name,
            'permission': permission
        }
        instance = cls(**kwargs)
        instance(method='put')
        msg = 'Permission of [{0}] in [{1}] has been changed to [{2}]'.format(user_name, repo_slug, permission)
        return BBApi.SUCCESS, msg

if __name__ == '__main__':
    """print BitBucket.get_projects().json()
    
     """