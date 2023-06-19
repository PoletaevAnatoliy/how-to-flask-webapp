from hashlib import sha256

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash


class User(UserMixin):
    """
    Пользователь, зарегистрированный в системе.
    О пользователе известны login и email.
    Для проверки пароля можно использовать метод check_password.
    """

    def __init__(self, id_, login, email, password_hash):
        self.id = id_
        self.login = login
        self.email = email
        self.password_hash = password_hash

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    @staticmethod
    def generate_password_hash(password: str) -> str:
        return generate_password_hash(password)

    def get_verification_code(self) -> str:
        return sha256(self.email.encode("utf-8")).hexdigest()[:8].upper()

    def is_verification_code_valid(self, verification_code: str) -> bool:
        return verification_code == self.get_verification_code()

    def __eq__(self, other):
        return isinstance(other, type(self)) and\
            self.id == other.id and\
            self.login == other.login and\
            self.email == other.email
