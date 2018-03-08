import sys
import os
import pytest

here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, here + '/../ansible/jira_roles')

from module_utils.jira_core import Jira

@pytest.fixture
def bb_interface():
    return Jira

# def test_projects_valid_email(bb_interface):
#     assert bb_interface._valid_email("ustglobal@gmail")
#
# def test_projects_add_user(bb_interface):
#     function_check = bb_interface.add_user("lathangi", "THGJDGFNHB", "lathangiust", "lathangi@ustglobal")
#     assert function_check[0] == True
#
# def test_projects_create_project(bb_interface):
#     function_check = bb_interface.create_project('Honorsamsung','UNASSIGNED','business','devika')
#     assert function_check[0] == True
#
#
# def test_projects_get_users(bb_interface):
#     assert bb_interface.get_users('lathangi')
#
#
def test_projects_get_projects(bb_interface):
    assert bb_interface.get_projects('FANDDANDQ')!= None
#
#
# def test_projects_get_all_projects(bb_interface):
#     assert bb_interface.get_all_projects('android')!= None
#
