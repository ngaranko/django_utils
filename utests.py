#django_utils/utests.py

from django.contrib.auth.models import User
from django.test import TestCase
from django.test.client import Client
from django.db import transaction

class FastClient(Client):
    classical = True
    def __init__(self, *args, **kwargs):
        super(FastClient, self).__init__(*args, **kwargs)
        self.test = None

    def get(self, *args, **kwargs):
        """Proceed with GET request
        If not classical test, commits transaction
        """
        result = super(FastClient, self).get(*args, **kwargs)

        if not self.classical:
            transaction.commit()

        return result

    def post(self, *args, **kwargs):
        """Proceed with POST request
        If not classical test, commits transaction
        """
        result = super(FastClient, self).post(*args, **kwargs)

        if not self.classical:
            transaction.commit()
        return result

class FastTestCase(TestCase):
    """Fast test case class
    Do not fushes database before every test case run,
    unless 'classical' is set to True
    """
    fixtures = []
    classical = False

    def _fixture_setup(self):
        """Hook around _pre_setup, will not allow to re-reload
        data each time testcase.test is running"""

        if not self.classical:
            try:
                User.objects.get(username='testuser')
            except User.DoesNotExist:
                # Loading fixtures
                super(FastTestCase, self)._fixture_setup()
        else:
            super(FastTestCase, self)._fixture_setup()

    def _fixture_teardown(self, forced=False):
        """Hook around _fixture_teardown"""
        if forced or self.classical:
            super(FastTestCase, self)._fixture_teardown()

    def _post_teardown(self):
        """Hook around _post_teardown
        disables closing of database connection"""
        if self.classical:
            super(FastTestCase, self)._post_teardown()

    def test_zzzzzzzzzzzz_teardown(self):
        if not self.classical:
            # Tearing down DB
            self._fixture_teardown(True)

