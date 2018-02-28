#!/usr/bin/python

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = '''
---
module: bitbucket_permission

short_description: Module to manage user permissions in bitbucket

version_added: "2.4"

description:
    - "Module to manage user permissions in bitbucket"

options:
    project:
        description:
            - Project to be used
        required: false
    repo:
        description:
            - Repo to be used
        required: false
    user:
        description:
            - User whose permission to be set/changed
        required: true
    permission:
        description:
            - Permission level to be set
        required: true
author:
    - Gopakumar Gopinathan (gopakumar.gopinathan@ust-global.com)
'''

EXAMPLES = '''
# Set permission for a user
- name: Set permission for a user in a project
  bitbucket_permission:
    project: test_project
    user: testuser
    permission: w

- name: Set permission for a user in a repo
  bitbucket_permission:
    project: test_project
    repo: test_repo
    user: testuser
    permission: w
'''


from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.bitbucket_core import BitBucket, BBApi


def run_module():
    module_args = dict(
        project=dict(type='str', required=False),
        user=dict(type='str', required=True),
        repo=dict(type='str', required=False),
        permission=dict(type='str', required=True, choices=['r', 'w', 'a'])
    )

    result = dict(
        changed=False,
        message='',
        meta=None

    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    if module.check_mode:
        return result

    project = module.params.get('project')
    repo = module.params.get('repo')
    user = module.params.get('user')
    permission = module.params.get('permission')
    try:
        if project and repo:
            permission_map = {
                'r': BBApi.repo_read,
                'w': BBApi.repo_write,
                'a': BBApi.repo_admin
            }
            status, msg = BitBucket.grant_repo_permission(project, repo, user,
                                                          permission=permission_map[permission])
            result['changed'] = status
            result['message'] = msg
        elif project and not repo:
            permission_map = {
                'r': BBApi.project_read,
                'w': BBApi.project_write,
                'a': BBApi.project_admin
            }
            status, msg = BitBucket.grant_project_permission(project, user,
                                                             permission=permission_map[permission])
            result['changed'] = status
            result['message'] = msg
    except Exception as e:
        result['message'] = 'Failed: {}'.format(str(e))
        module.fail_json(msg='Permission cant be set', **result)

    module.exit_json(**result)

def main():
    run_module()

if __name__ == '__main__':
    main()
