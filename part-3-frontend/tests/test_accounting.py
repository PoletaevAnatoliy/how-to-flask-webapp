from tests import BaseTestCase
from webapp import register_user, find_user_with_email
from webapp.db.accounting import AlreadyRegisteredException


class AccountingTests(BaseTestCase):

    def test_registration(self):
        login, email, password = "ivan", "ivan@mail.com", "qwerty123"
        with self.app.app_context():
            self.create_data()
            self.assertIsNone(find_user_with_email(email))
            register_user(login, email, password)
            user = find_user_with_email(email)
            self.assertEqual(login, user.login)
            self.assertEqual(email, user.email)
            self.assertTrue(user.check_password(password))

    def test_login_duplication(self):
        first_login, first_email, first_password = "ivan", "ivan@mail.com", "qwerty123"
        second_login, second_email, second_password = "ivan", "ivanov@mail.com", "asdfg456"
        with self.app.app_context():
            self.create_data()
            register_user(first_login, first_email, first_password)
            self.assertRaises(AlreadyRegisteredException,
                              register_user, second_login, second_email, second_password)

    def test_email_duplication(self):
        first_login, first_email, first_password = "ivan", "ivan@mail.com", "qwerty123"
        second_login, second_email, second_password = "ivanov", "ivan@mail.com", "asdfg456"
        with self.app.app_context():
            self.create_data()
            register_user(first_login, first_email, first_password)
            self.assertRaises(AlreadyRegisteredException,
                              register_user, second_login, second_email, second_password)
