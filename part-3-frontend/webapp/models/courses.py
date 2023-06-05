from PIL import Image as PILImage

from webapp.models.accounting import User


class Course:
    """
    Курс, созданный пользователем (author) и хранящийся в системе.
    Содержит информацию о названии (title) и описании курса (description).
    """

    def __init__(self, id_: int, title: str, description: str, author: User):
        self.id = id_
        self.title = title
        self.description = description
        self.author = author

    def __eq__(self, other):
        return isinstance(other, type(self)) and\
            self.id == other.id and\
            self.title == other.title and\
            self.description == other.description and\
            self.author == other.author


class Article:
    """
    Статья, добавленная пользователем (author) и хранящаяся в системе.
    Содержит информацию о названии (title), а также текст статьи (text).
    """

    def __init__(self, id_: int, title: str, text: str, author: User):
        self.id = id_
        self.title = title
        self.text = text
        self.author = author

    def __eq__(self, other):
        return isinstance(other, type(self)) and \
            self.id == other.id and \
            self.title == other.title and \
            self.text == other.text and \
            self.author == other.author


class Comment:
    """
    Комментарий, оставленный пользователем (author) и хранящийся в системе.
    СОдержит информацию о тексте комментария (text).
    """

    def __init__(self, id_: int, text: str, author: User):
        self.id = id_
        self.text = text
        self.author = author

    def __hash__(self):
        return hash(self.id) + hash(self.text)

    def __eq__(self, other):
        return isinstance(other, type(self)) and \
            self.id == other.id and \
            self.text == other.text and \
            self.author == other.author


class Image:
    """
    Изображение, добавленное пользователем (author) к одной из статей и хранящееся в системе.
    Само изображение хранится с помощью Image из библиотеки Pillow
    """

    def __init__(self, id_: int, image: PILImage, author: User):
        self.id = id_
        self.image = image
        self.author = author

    def _to_rgb(self):
        return self.image.getdata()

    def __eq__(self, other):
        return isinstance(other, type(self)) and\
            self.id == other.id and\
            self.author == other.author and\
            self._to_rgb() == other._to_rgb()
