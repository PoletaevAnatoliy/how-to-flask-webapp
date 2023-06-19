import unittest

from webapp import create_app
from webapp.db import init_db


class BaseTestCase(unittest.TestCase):

    def setUp(self):
        self.app = create_app(config={
            "DATABASE": ":memory:",
            "TEST": True
        })

    def create_data(self):
        init_db()
