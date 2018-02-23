#!/usr/bin/python
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.jira_core import Jira, JiraApi




ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = '''
---
module: jira_user

short_description: Module to manage user creation in jira

version_added: "2.4"

description:
    - "Module to manage user creation in jira"

options:
    name:
        description:
            - User to be created
        required: true
    display_name:
        description:
            - Name to be displayed for the user
        required: true
    email_address:
        description:
            - Email id of the user
        required: true

author:
    - Gopakumar Gopinathan (gopakumar.gopinathan@ust-global.com)
'''

EXAMPLES = '''
# Create a user
- name: Create a user
    jira_user:
    name: test_user
    display_name: Test User
    email_address: test@test
'''


def run_module():

    module_args = dict(
        name=dict(type='str', required=True),
        display_name=dict(type='str', required=True),
        email_address=dict(type='str', required=True)
    )

    result = dict(
        changed=False,
        message='',
        meta=None,
        failed=False
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    if module.check_mode:
        return result

    name = module.params.get('name')
    display_name = module.params.get('display_name')
    email_address = module.params.get('email_address')

    try:
        pwd = Jira.password_gen()
        res, msg = Jira.add_user(name, pwd, display_name, email_address)

        if res == JiraApi.EXISTS:
            result['changed'] = False

        elif res:
            result['changed'] = True
            result['pwd'] = pwd
        result['message'] = msg

    except Exception as e:
            result['failed'] = True
            result['message'] = 'Failed: {}'.format(str(e))
            module.fail_json(msg='User creation is failed', **result)

    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
