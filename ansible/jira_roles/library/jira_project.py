#!/usr/bin/python
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.jira_core import Jira,JiraApi


ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = '''
---
module: jira_project

short_description: Module to create a  project in jira

version_added: "2.4"

description:
    - "Module to manage project creation in jira"

options:
    project:
        description:
            - Project to be used/created
        required: true
    key:
        key:
            - Some description about the project to be created
        required: false
        
        
    assigneeType:
        assigneeType:
          -assigneetype can be PROJECT_LEAD OR UNASSIGNED
     
    projectTypeKey:
        projectTypeKey :
                 specify project type
                 
    lead:
        lead:
            name of the lead
        
        

author:
    - Gopakumar Gopinathan (gopakumar.gopinathan@ust-global.com)
'''

EXAMPLES = '''
# Create a project
- name: Create a project
  jira_project:
    project: test_project
    key: TEST
    assigneeType:project_lead
    projectTypeKey:bussiness
    lead:xyz
    
'''


def run_module():
    module_args = dict(
        projectName=dict(type='str', required=True),
        assigneeType=dict(type='str', required=True),
        projectTypeKey=dict(type='str', required=True),
        lead=dict(type='str', required=True)
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

    projectname = module.params.get('projectName')
    assigneetype = module.params.get('assigneeType')
    projectypekey = module.params.get('projectTypeKey')
    lead = module.params.get('lead')

    try:
        if projectname:

            res, msg = Jira.create_project(projectname, assigneetype, projectypekey, lead)
            if res == JiraApi.EXISTS:
                result['changed'] = False
            elif res==JiraApi.FAILED:
                result['changed'] = False
            elif res:
                result['changed'] = True
            result['message'] = msg

    except Exception as e:

        result['message'] = 'project creation is Failed: {}'.format(str(e))
        module.fail_json(msg='Project creation is failed', **result)

    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
