from tests import BaseTestCase
from webapp.db.accounting import register_user, \
    find_user_with_email
from webapp.db.notifications import UserAlreadyConnectedToTelegram, \
    TelegramAlreadyConnectedToAnotherUser, connect_telegram, disconnect_telegram, \
    find_telegram_for, get_pending_notifications, add_notification, mark_delivered


class NotificationTests(BaseTestCase):

    def create_data(self):
        super().create_data()
        first_user_login, first_user_email, first_user_password = "ivan", "ivan@mail.com", "qwerty123"
        second_user_login, second_user_email, second_user_password = "ivanov", "ivanov@mail.com", "asdfg456"
        register_user(first_user_login, first_user_email, first_user_password)
        register_user(second_user_login, second_user_email, second_user_password)
        self.first_user = find_user_with_email(first_user_email)
        self.second_user = find_user_with_email(second_user_email)

    def test_telegram_account_connection(self):
        account_user_id, account_username = 123456789, "Ivan"
        with self.app.app_context():
            self.create_data()
            connect_telegram(self.first_user, account_user_id, account_username)
            account = find_telegram_for(self.first_user)
            self.assertEqual(account_user_id, account.telegram_user_id)
            self.assertEqual(account_username, account_username)
            self.assertIsNone(find_telegram_for(self.second_user))

    def test_telegram_account_removal(self):
        account_user_id, account_username = 123456789, "Ivan"
        with self.app.app_context():
            self.create_data()
            connect_telegram(self.first_user, account_user_id, account_username)
            disconnect_telegram(self.first_user, find_telegram_for(self.first_user))
            self.assertIsNone(find_telegram_for(self.first_user))
            self.assertIsNone(find_telegram_for(self.second_user))

    def test_telegram_accounts_exchange(self):
        account_user_id, account_username = 123456789, "Ivan"
        another_account_user_id, another_account_username = 123456709, "Peter"
        with self.app.app_context():
            self.create_data()
            connect_telegram(self.first_user, account_user_id, account_username)
            connect_telegram(self.second_user, another_account_user_id, another_account_username)
            disconnect_telegram(self.first_user, find_telegram_for(self.first_user))
            disconnect_telegram(self.second_user, find_telegram_for(self.second_user))
            connect_telegram(self.first_user, another_account_user_id, another_account_username)
            connect_telegram(self.second_user, account_user_id, account_username)
            another_account = find_telegram_for(self.first_user)
            account = find_telegram_for(self.second_user)
            self.assertEqual(account_user_id, account.telegram_user_id)
            self.assertEqual(account_username, account.username)
            self.assertEqual(another_account_user_id, another_account.telegram_user_id)
            self.assertEqual(another_account_username, another_account.username)

    def test_telegram_account_duplication(self):
        account_user_id, account_username = 123456789, "Ivan"
        another_account_id, another_account_username = 123456709, "Peter"
        with self.app.app_context():
            self.create_data()
            connect_telegram(self.first_user, account_user_id, account_username)
            self.assertRaises(UserAlreadyConnectedToTelegram,
                              connect_telegram, self.first_user, another_account_id, another_account_username)
            self.assertRaises(TelegramAlreadyConnectedToAnotherUser,
                              connect_telegram, self.second_user, account_user_id, account_username)

    def test_verification_code(self):
        with self.app.app_context():
            self.create_data()
            verification_code = self.first_user.get_verification_code()
            another_verification_code = self.second_user.get_verification_code()
            first_user = find_user_with_email(self.first_user.email)
            second_user = find_user_with_email(self.second_user.email)
            self.assertTrue(first_user.is_verification_code_valid(verification_code))
            self.assertTrue(second_user.is_verification_code_valid(another_verification_code))
            self.assertFalse(first_user.is_verification_code_valid(another_verification_code))
            self.assertFalse(second_user.is_verification_code_valid(verification_code))

    def test_notifications_creation(self):
        first_notification_text, first_notification_link = "Notification!", "www.google.com"
        second_notification_text = "Another notification"
        third_notification_text, third_notification_link = "Third notification", "www.yandex.ru"
        with self.app.app_context():
            self.create_data()
            self.assertEqual(0, len(get_pending_notifications()))
            add_notification(self.first_user, first_notification_text, first_notification_link)
            add_notification(self.first_user, second_notification_text)
            add_notification(self.second_user, third_notification_text, third_notification_link)
            first_notification, second_notification, third_notification = get_pending_notifications()
            self.assertEqual(first_notification_text, first_notification.text)
            self.assertEqual(first_notification_link, first_notification.link)
            self.assertEqual(self.first_user, first_notification.user)
            self.assertEqual(second_notification_text, second_notification.text)
            self.assertIsNone(second_notification.link)
            self.assertEqual(self.first_user, second_notification.user)
            self.assertEqual(third_notification_text, third_notification.text)
            self.assertEqual(third_notification_link, third_notification.link)
            self.assertEqual(self.second_user, third_notification.user)

    def test_notifications_text_duplication(self):
        first_notification_text, first_notification_link = "Notification!", "www.google.com"
        second_notification_text = "Notification"
        third_notification_text, third_notification_link = "Notification!", "www.google.com"
        with self.app.app_context():
            self.create_data()
            self.assertEqual(0, len(get_pending_notifications()))
            add_notification(self.first_user, first_notification_text, first_notification_link)
            add_notification(self.first_user, second_notification_text)
            add_notification(self.first_user, third_notification_text, third_notification_link)
            first_notification, second_notification, third_notification = get_pending_notifications()
            self.assertEqual(first_notification_text, first_notification.text)
            self.assertEqual(first_notification_link, first_notification.link)
            self.assertEqual(self.first_user, first_notification.user)
            self.assertEqual(second_notification_text, second_notification.text)
            self.assertIsNone(second_notification.link)
            self.assertEqual(self.first_user, second_notification.user)
            self.assertEqual(third_notification_text, third_notification.text)
            self.assertEqual(third_notification_link, third_notification.link)
            self.assertEqual(self.first_user, third_notification.user)
            self.assertNotEquals(first_notification, second_notification)
            self.assertNotEqual(first_notification, third_notification)
            self.assertNotEquals(second_notification, third_notification)

    def test_notifications_delivering_marking(self):
        first_notification_text, first_notification_link = "Notification!", "www.google.com"
        second_notification_text = "Another notification"
        third_notification_text, third_notification_link = "Third notification", "www.yandex.ru"
        with self.app.app_context():
            self.create_data()
            self.assertEqual(0, len(get_pending_notifications()))
            add_notification(self.first_user, first_notification_text, first_notification_link)
            add_notification(self.first_user, second_notification_text)
            add_notification(self.second_user, third_notification_text, third_notification_link)
            first_notification, second_notification, third_notification = get_pending_notifications()
            mark_delivered(second_notification)
            first_notification, third_notification = get_pending_notifications()
            self.assertEqual(first_notification_text, first_notification.text)
            self.assertEqual(first_notification_link, first_notification.link)
            self.assertEqual(self.first_user, first_notification.user)
            self.assertEqual(third_notification_text, third_notification.text)
            self.assertEqual(third_notification_link, third_notification.link)
            self.assertEqual(self.second_user, third_notification.user)
            mark_delivered(third_notification)
            first_notification, *_ = get_pending_notifications()
            self.assertEqual(first_notification_text, first_notification.text)
            self.assertEqual(first_notification_link, first_notification.link)
            self.assertEqual(self.first_user, first_notification.user)
            mark_delivered(first_notification)
            self.assertEqual(0, len(get_pending_notifications()))
