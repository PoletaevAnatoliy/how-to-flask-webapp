from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

from webapp.db import get_connection


class User(UserMixin):
    def __init__(self, id_, login, email, password_hash):
        self.id = id_
        self.login = login
        self.email = email
        self.password_hash = password_hash


def register_user(login: str, email: str, password: str):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("""
        INSERT INTO users (login, email, password_hash)
        VALUES (?, ?, ?);
    """, (login, email, generate_password_hash(password)))
    connection.commit()


def user_with_email(email: str) -> User:
    record = get_connection().cursor().execute("""
        SELECT id, login, email, password_hash
        FROM users
        WHERE email = ?;
    """, (email,)).fetchone()
    return User(record["id"], record["login"], record["email"], record["password_hash"])


def user_with_id(id_: int) -> User:
    record = get_connection().cursor().execute("""
        SELECT id, login, email, password_hash
        FROM users
        WHERE id = ?;
    """, (id_,)).fetchone()
    return User(record["id"], record["login"], record["email"], record["password_hash"])


def is_correct_password(user: User, password: str) -> bool:
    return check_password_hash(user.password_hash, password)
