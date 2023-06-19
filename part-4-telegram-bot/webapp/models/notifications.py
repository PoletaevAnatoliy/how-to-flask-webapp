from webapp.models.accounting import User


class TelegramAccount:
    """
    Telegram-аккаунт, который был прикреплён одним из пользователей к своему аккаунту на сайте.
    Об аккаунте известны id пользователя в Telegram и имя пользователя в Telegram (username).
    """

    def __init__(self, id_: int, telegram_user_id: int, username: str, user: User):
        self.id = id_
        self.telegram_user_id = telegram_user_id
        self.username = username
        self.user = user

    def to_json(self):
        return {
            "id": self.id,
            "telegram-id": self.telegram_user_id,
            "username": self.username,
            "user-id": self.user.id
        }

    def __eq__(self, other):
        if not isinstance(other, TelegramAccount):
            return False
        return self.telegram_user_id == other.telegram_user_id\
            and self.username == other.username


class Notification:
    """
    Уведомление о событии, которое должно быть отправлено пользователю сайта.
    Об уведомлении известны его текст и (опциональная) ссылка на страницу сайта, на которой можно просмотреть подробности
    """

    def __init__(self, id_: int, text: str, user: User, link: str = None):
        self.id = id_
        self.text = text
        self.link = link
        self.user = user

    def to_json(self):
        return {
            "id": self.id,
            "text": self.text,
            "link": self.link,
            "user-id": self.user.id
        }

    def __eq__(self, other):
        if not isinstance(other, Notification):
            return False
        return self.id == other.id and self.text == other.text \
            and self.link == other.link and self.user == other.user
