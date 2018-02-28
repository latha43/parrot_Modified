import sys
import os

import pytest

here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, here + '/../ansible/bb_roles')

from utils.bitbucket_core import BitBucket

@pytest.fixture
def bb_interface():
    return BitBucket


def test_projects(bb_interface):
    assert bb_interface.is_project_existing('test')


