import sqlite3

from webapp import find_user_with_id
from webapp.db import get_connection
from webapp.models.accounting import User
from webapp.models.notifications import TelegramAccount, Notification


class UserAlreadyConnectedToTelegram(Exception):
    pass


class TelegramAlreadyConnectedToAnotherUser(Exception):
    pass


def connect_telegram(user: User, account_id: int, account_username: str):
    """
    Связать Telegram-аккаунт с аккаунтом пользователя на сайте.

    Если для переданного пользователя уже есть связанный Telegram-аккаунт, будет выброшено исключение UserAlreadyConnectedToTelegram

    Если Telegram-аккаунт с заданными параметрами уже связан с другим пользователем, будет выброшено исключение TelegramAlreadyConnectedToAnotherUser
    :param user: пользователь, к аккаунту которого будет привязан аккаунт Telegram
    :param account_id: id аккаунта в Telegram
    :param account_username: имя пользователя в Telegram
    """
    if find_telegram_for(user) is not None:
        raise UserAlreadyConnectedToTelegram()
    connection = get_connection()
    try:
        connection.cursor().execute("""
            INSERT INTO telegram_accounts(telegram_user_id, username, user_id)
            VALUES (?, ?, ?);
        """, (account_id, account_username, user.id))
    except sqlite3.IntegrityError:
        raise TelegramAlreadyConnectedToAnotherUser()
    connection.commit()


def disconnect_telegram(user: User, telegram: TelegramAccount):
    """
    Отвязать Telegram-аккаунт от аккаунта пользователя на сайте
    :param user: пользователь, для которого отвязывается аккаунт
    :param telegram: Telegram-аккаунт, который будет отвязан от пользователя
    """
    connection = get_connection()
    connection.cursor().execute("""
        DELETE FROM telegram_accounts
        WHERE id = ? AND user_id = ?;
    """, (telegram.id, user.id))
    connection.commit()


def find_telegram_for(user: User) -> TelegramAccount | None:
    """
    Найти и получить Telegram-аккаунт, привязанный к данному пользователю
    :param user: пользователь, для которого производится поиск
    :return: Telegram-аккаунт или None, если к данному пользователю не привязан аккаунт Telegram
    """
    record = get_connection().cursor().execute("""
        SELECT id, telegram_user_id, username
        FROM telegram_accounts
        WHERE user_id = ?;
    """, (user.id,)).fetchone()
    if record is None:
        return None
    return TelegramAccount(record["id"], record["telegram_user_id"],
                           record["username"], user)


def find_telegram_with_id(telegram_id: int) -> TelegramAccount | None:
    """
    Найти и получить Telegram-аккаунт с данным telegram_id
    :param telegram_id: id пользователя в Telegram
    :return: аккаунт Telegram или None, если Telegram-аккаунт с данным id не известен системе
    """
    record = get_connection().cursor().execute("""
        SELECT id, username, user_id
        FROM telegram_accounts
        WHERE telegram_user_id = ?;
    """, (telegram_id,)).fetchone()
    if record is None:
        return None
    return TelegramAccount(record["id"], telegram_id, record["username"],
                           find_user_with_id(record["user_id"]))


def add_notification(for_user: User, text: str, link: str = None):
    """
    Создать в базе данных запись о том,
    что пользователю нужно отправить уведомление с заданным текстом и, опционально, ссылкой.
    :param for_user: пользователь-адресат уведомления
    :param text: текст уведомления
    :param link: ссылка, которая будет приложена к уведомлению
    """
    connection = get_connection()
    connection.cursor().execute("""
        INSERT INTO notifications (text, link, user_id)
        VALUES (?, ?, ?); 
    """, (text, link, for_user.id))
    connection.commit()


def find_notification_with_id(id_: int) -> Notification | None:
    """
    Найти и получить уведомление с данным id
    :param id_: id уведомления
    :return: уведомление или None, если уведомление с данным id не известно системе
    """
    record = get_connection().cursor().execute("""
        SELECT id, text, link, user_id 
        FROM notifications
        WHERE id = ?;
    """, (id_,)).fetchone()
    if record is None:
        return None
    return Notification(record["id"], record["text"],
                        find_user_with_id(record["user_id"]), record["link"])


def get_pending_notifications() -> list[Notification]:
    """
    Получить список всех ещё не доставленных уведомлений, от более старых к более новым.
    """
    records = get_connection().cursor().execute("""
        SELECT id, text, link, user_id
        FROM notifications
        WHERE NOT delivered
        ORDER BY id;
    """).fetchall()
    return [Notification(record["id"], record["text"],
                         find_user_with_id(record["user_id"]), record["link"])
            for record in records]


def mark_delivered(notification: Notification):
    """
    Отметить уведомление как доставленное
    :param notification: уведомление, которое было доставлено
    """
    connection = get_connection()
    connection.cursor().execute("""
        UPDATE notifications
        SET delivered = 1
        WHERE id = ?;
    """, (notification.id,))
    connection.commit()
