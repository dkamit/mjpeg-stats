"""Testing utilities for LSS Test Tool."""

from lss.cli.main import TestApp
from cement.utils.test import *

class TestCase(CementTestCase):
    app_class = TestApp

    def setUp(self):
        """Override setup actions (for every test)."""
        super(TestCase, self).setUp()

    def tearDown(self):
        """Override teardown actions (for every test)."""
        super(TestCase, self).tearDown()

