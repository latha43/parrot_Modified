#!/usr/bin/python

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = '''
---
module: bitbucket_project

short_description: Module to manage project creation in bitbucket

version_added: "2.4"

description:
    - "Module to manage project creation in bitbucket"

options:
    project:
        description:
            - Project to be used/created
        required: true
    desc:
        description:
            - Some description about the project to be created
        required: false

author:
    - Gopakumar Gopinathan (gopakumar.gopinathan@ust-global.com)
'''

EXAMPLES = '''
# Create a project
- name: Create a project
  bitbucket_project:
    project: test_project
    desc: Dummy project
'''


from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.bitbucket_core import BitBucket, BBApi


def run_module():
    module_args = dict(
        project=dict(type='str', required=True),
        desc=dict(type='str', required=True)
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
    description = module.params.get('desc')
    try:
        if project and description:
            res, msg = BitBucket.add_project(project, description)
            if res == BBApi.EXISTS:
                result['changed'] = False
            elif res:
                result['changed'] = True
            result['message'] = msg
    except Exception as e:
        result['message'] = 'Failed: {}'.format(str(e))
        module.fail_json(msg='Project/Repository creation is failed', **result)

    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
