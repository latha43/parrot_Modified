#!/usr/bin/python

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = '''
---
module: bitbucket_repo

short_description: Module to manage repository creation in bitbucket

version_added: "2.4"

description:
    - "Module to manage repository creation in bitbucket"

options:
    project:
        description:
            - Project to be used/created
        required: true
    repo:
        description:
            - Repository name to be created
        required: true

author:
    - Gopakumar Gopinathan (gopakumar.gopinathan@ust-global.com)
'''

EXAMPLES = '''
# Create a repository
- name: Create a repository
  bitbucket_repo:
    project: TEST_PROJECT
    repo: My Repo
'''


from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.bitbucket_core import BitBucket, BBApi


def run_module():
    module_args = dict(
        project=dict(type='str', required=True),
        repo=dict(type='str', required=True)
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
    try:
        res, msg = BitBucket.add_repo(project, repo)
        if res == BBApi.EXISTS:
            result['changed'] = False
        elif res:
            result['changed'] = True
        result['message'] = msg
    except Exception as e:
        result['message'] = 'Failed: {}'.format(str(e))
        module.fail_json(msg='Repository creation is failed', **result)

    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
