import sqlite3

from webapp.db import get_connection
from webapp.models.accounting import User


class AlreadyRegisteredException(Exception):
    pass


def register_user(login: str, email: str, password: str):
    """
    Зарегистрировать в системе нового пользователя.
    В случае, если пользователь с таким логином или email уже существует,
        будет выброшено AlreadyRegistredException
    :param login: логин пользователя
    :param email: email пользователя
    :param password: пароль пользователя
    """
    connection = get_connection()
    cursor = connection.cursor()
    # более правильный способ, но требует блокировки БД
    # if find_user_with_email(email) or find_user_with_login(login):
    #     raise AlreadyRegisteredException()
    try:
        cursor.execute("""
            INSERT INTO users (login, email, password_hash)
            VALUES (?, ?, ?);
        """, (login, email, User.generate_password_hash(password)))
    except sqlite3.IntegrityError as e:
        if "users.email" in str(e) or "users.login" in str(e):
            raise AlreadyRegisteredException()
    connection.commit()


def find_user_with_email(email: str) -> User | None:
    """
    Найти и получить пользователя с указанным адресом электронной почты
    :param email: адрес электронной почты
    :return: пользователь или None, если пользователя с заданным email не существует
    """
    record = get_connection().cursor().execute("""
        SELECT id, login, email, password_hash
        FROM users
        WHERE email = ?;
    """, (email,)).fetchone()
    if record is None:
        return None
    return User(record["id"], record["login"], record["email"], record["password_hash"])


def find_user_with_id(id_: int) -> User | None:
    """
    Найти и получить пользователя с указанным id
    :param id_:
    :return: пользователь или None, если пользователя с заданным id не существует
    """
    record = get_connection().cursor().execute("""
        SELECT id, login, email, password_hash
        FROM users
        WHERE id = ?;
    """, (id_,)).fetchone()
    if record is None:
        return None
    return User(record["id"], record["login"], record["email"], record["password_hash"])


