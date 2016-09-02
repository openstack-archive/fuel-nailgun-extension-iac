import os

from oslotest import base

from fuel_external_git import settings


class TestCase(base.BaseTestCase):

    """Test case base class for all unit tests."""
    def setUp(self):
        super(TestCase, self).setUp()
        self.config = settings.GitExtensionSettings().config
        self.cfg_sample_dir = os.path.join(os.path.dirname(__file__), 'cfgs')
