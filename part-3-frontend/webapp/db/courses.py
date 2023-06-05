import io
import sqlite3

from PIL import Image as PILImage

from webapp.db import get_connection
from webapp.db.accounting import find_user_with_id
from webapp.models.accounting import User
from webapp.models.courses import Course, Article, Image, Comment


class StudentsCannotCreateArticles(Exception):
    pass


class StudentsCannotEditArticles(Exception):
    pass


class StudentsCannotDeleteComments(Exception):
    pass


class StudentsCannotReplyAtComments(Exception):
    pass


class CourseAlreadyExists(Exception):
    pass


def add_course(title: str, description: str, author: User):
    """
    Добавляет новый курс от имени переданного пользователя.
    В случае, если курс с таким названием уже существует,
    будет выброшено исключение CourseAlreadyExists
    :param title: название курса
    :param description: описание курса
    :param author: пользователь, создающий курс
    """
    connection = get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("""
            INSERT INTO courses (title, description, author_id)
            VALUES (?, ?, ?);
        """, (title, description, author.id))
    except sqlite3.IntegrityError:
        raise CourseAlreadyExists()
    connection.commit()


def find_all_courses() -> list[Course]:
    """
    Получить список курсов, созданных в системе
    :return: список всех курсов в порядке создания (от старых к новым)
    """
    cursor = get_connection().cursor()
    records = cursor.execute("""
        SELECT id, title, description, author_id
        FROM courses
        ORDER BY id;
    """).fetchall()
    return [Course(r["id"], r["title"],
                   r["description"], find_user_with_id(r["author_id"]))
            for r in records]


def find_courses_created_by(author: User) -> list[Course]:
    """
    Получить список курсов, созданных данным пользователем
    :param author: пользователь-автор курсов
    :return: список всех курсов автора в порядке создания (от старых к новым)
    """
    records = get_connection().cursor().execute("""
        SELECT id, title, description
        FROM courses
        WHERE author_id = ?
        ORDER BY id;
    """, (author.id,))
    return [Course(r["id"], r["title"], r["description"], author)
            for r in records]


def find_course_with_id(id_: int) -> Course | None:
    """
    Курс с заданным id или None, если курса с таким id не существует
    :param id_: id курса
    :return: искомый Course или None
    """
    cursor = get_connection().cursor()
    record = cursor.execute("""
        SELECT id, title, description, author_id
        FROM courses
        WHERE id = ?;
    """, (id_,)).fetchone()
    if record is None:
        return None
    return Course(record["id"], record["title"],
                  record["description"], find_user_with_id(record["author_id"]))


def add_to_favored_courses(course: Course, user: User):
    """
    Добавить переданный курс в список избранных для заданного пользователя
    :param course: добавляемый в избранное курс
    :param user: пользователь, для которого курс добавляется в избранное
    """
    connection = get_connection()
    connection.cursor().execute("""
        INSERT INTO courses_favored_by_users (course_id, user_id)
        VALUES (?, ?);
    """, (course.id, user.id))
    connection.commit()


def remove_from_favored_courses(course: Course, user: User):
    """
    Удалить переданный курс из списка избранных заданным пользователем
    :param course: добавляемый в избранное курс
    :param user: пользователь, для которого курс добавляется в избранное
    """
    connection = get_connection()
    connection.cursor().execute("""
        DELETE FROM courses_favored_by_users
        WHERE course_id = ? AND user_id = ?;
    """, (course.id, user.id))
    connection.commit()


def find_courses_favored_by(user: User) -> list[Course]:
    """
    Получить список курсов, добавленных данным пользователем в список избранных
    :param user: пользователь, избранные курсы которого ищутся
    :return: список курсов, "избранных" данным пользователем, в порядке создания (от старых к новым)
    """
    cursor = get_connection().cursor()
    records = cursor.execute("""
        SELECT c.id AS c_id, c.title AS c_title, c.description AS c_description,
            c.author_id AS c_author_id
        FROM courses_favored_by_users AS c_to_u
            JOIN users AS u ON c_to_u.user_id = u.id
            JOIN courses AS c ON c_to_u.course_id = c.id
        WHERE u.id = ?;
    """, (user.id,)).fetchall()
    return [Course(r["c_id"], r["c_title"], r["c_description"],
                   find_user_with_id(r["c_author_id"]))
            for r in records]


def add_article(title: str, text: str, course: Course, author: User):
    """
    Добавить новую статью в заданный курс.
    В случае, если статью пытается добавить пользователь, не являющийся автором курса,
        будет выброшено StudentsCannotCreateArticles
    :param title: название добавляемой статьи
    :param text: текст добавляемой статьи
    :param course: курс, для которого добавляется статья
    :param author: пользователь, добавляющий статью
    """
    if author != course.author:
        raise StudentsCannotCreateArticles()
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("""
        INSERT INTO articles (title, text, course_id, author_id)
        VALUES (?, ?, ?, ?);
    """, (title, text, course.id, author.id))
    connection.commit()


def edit_article(article: Article, new_title: str, new_text: str, editor: User):
    """
    Отредактировать заданную статью, задав ей новый заголовок и текст
    В случае, если статью пытается отредактировать пользователь, не являющийся её автором,
        будет выброшено StudentsCannotEditArticles
    :param article: редактируемая статья (в исходном виде)
    :param new_title: новое название статьи
    :param new_text: новый текст статьи
    :param editor: пользователь, редактирующий статью
    """
    if editor != article.author:
        raise StudentsCannotEditArticles()
    connection = get_connection()
    connection.cursor().execute("""
        UPDATE articles
        SET title = ?, text = ?
        WHERE id = ?;
    """, (new_title, new_text, article.id))
    connection.commit()


def find_article_with_id(id_: int) -> Article | None:
    """
    Получить статью с заданным id
    :param id_:
    :return: статья или None, если статьи с заданным id не существует
    """
    cursor = get_connection().cursor()
    record = cursor.execute("""
        SELECT a.id as a_id, a.title as a_title, a.text as a_text, u.id as u_id
        FROM articles as a
            JOIN courses as c ON a.course_id=c.id
            JOIN users as u ON c.author_id=u.id
        WHERE a_id = ?;
    """, (id_,)).fetchone()
    if record is None:
        return None
    return Article(record["a_id"], record["a_title"], record["a_text"], find_user_with_id(record["u_id"]))


def find_articles_for(course: Course) -> list[Article]:
    """
    Получить список статей, добавленных для данного курса
    :param course: курс, статьи в котором получаются
    :return: список статей курса в порядке их добавления (от старых к новым)
    """
    cursor = get_connection().cursor()
    records = cursor.execute("""
        SELECT a.id as a_id, a.title as a_title, a.text as a_text, u.id as u_id
        FROM articles as a
            JOIN courses as c ON a.course_id=c.id
            JOIN users as u ON c.author_id=u.id
        WHERE c.id = ?
        ORDER BY a_id;
    """, (course.id,)).fetchall()
    return [Article(r["a_id"], r["a_title"], r["a_text"], find_user_with_id(r["u_id"]))
            for r in records]


def find_course_for_article(article: Article) -> Course | None:
    """
    Получить курс, которому принадлежит заданная статья
    В случае, если такого курса нет, вернуть None
    """
    article_record = get_connection().cursor().execute("""
        SELECT course_id
        FROM articles
        WHERE id = ?;
    """, (article.id,)).fetchone()
    if article_record is None:
        return None
    return find_course_with_id(article_record["course_id"])


def add_image(image: PILImage, article: Article, author: User):
    """
    Добавить в систему новое изображение
    :param image: добавляемое изображение в виде pillow Image
    :param article: статья, для которой добавляется изображение
    :param author: пользователь, добавляющий статью
    """
    connection = get_connection()
    connection.cursor().execute("""
        INSERT INTO images (image, author_id, article_id)
        VALUES (?, ?, ?);
    """, (_image_to_bytes(image), author.id, article.id))
    connection.commit()


def find_image_with_id(id_: int) -> Image | None:
    """
    Получить изображение с заданным id
    :param id_:
    :return: изображение — Image или None, если изображения с данным id в системе нет
    """
    record = get_connection().cursor().execute("""
        SELECT id, image, author_id
        FROM images
        WHERE id = ?;
    """, (id_,)).fetchone()
    if record is None:
        return None
    return Image(record["id"],
                 _image_from_bytes(record["image"]),
                 find_user_with_id(record["author_id"]))


def find_images_in(article: Article) -> list[Image]:
    """
    Получить изображения, добавленные для заданной статьи
    :param article:
    :return: изображения, добавленные для заданной статьи, в порядке добавления (от старых к новым)
    """
    records = get_connection().cursor().execute("""
        SELECT id, image, author_id
        FROM images
        WHERE article_id = ?;
    """, (article.id,)).fetchall()
    return [Image(r["id"],
                  _image_from_bytes(r["image"]),
                  find_user_with_id(r["author_id"]))
            for r in records]


def left_comment_for(text: str, article: Article, author: User):
    """
    Оставить комментарий к заданной статье
    :param text: текст комментария
    :param article: статья, для которой добавляется комментарий
    :param author: автор комментария
    """
    connection = get_connection()
    connection.cursor().execute("""
        INSERT INTO comments (text, parent_article_id, author_id)
        VALUES (?, ?, ?);
    """, (text, article.id, author.id))
    connection.commit()


def reply_at_comment(text: str, comment: Comment, author: User):
    """
    Оставить ответ к заданному комментарию.
    В случае, если комментарий пытается оставить не автор статьи,
        будет выброшено StudentsCannotReplyAtComments.
    :param text: текст ответа
    :param comment: комментарий, на который даётся ответ
    :param author: пользователь, оставляющий ответ на комментарий
    """
    article = find_article_comment_was_left_for(comment)
    if author != article.author:
        raise StudentsCannotReplyAtComments()
    connection = get_connection()
    connection.cursor().execute("""
        INSERT INTO comments (text, parent_comment_id, author_id)
        VALUES (?, ?, ?);
    """, (text, comment.id, author.id))
    connection.commit()


def delete_comment(comment: Comment, deleter: User):
    """
    Удалить заданный комментарий.
    В случае, если удалить комментарий пытается не автор статьи,
        к которой он был оставлен (или не автор исходной статьи, если удаляется ответ на комментарий),
        будет выброшено StudentsCannotDeleteComments
    :param comment: удаляемый комментарий
    :param deleter: пользователь, пытающийся удалить комментарий
    """
    article = find_article_comment_was_left_for(comment)
    if deleter != article.author:
        raise StudentsCannotDeleteComments()
    for reply in find_comments_replied_at(comment):
        delete_comment(reply, deleter)
    connection = get_connection()
    connection.cursor().execute("""
        UPDATE comments
        SET deleted = 1
        WHERE id = ?;
    """, (comment.id,))
    connection.commit()


def find_comment_with_id(id_: int) -> Comment | None:
    """
    Получить комментарий с заданным id
    :param id_:
    :return: комментарий или None, если комментария с заданным id нет в системе
    """
    record = get_connection().cursor().execute("""
        SELECT id, text, author_id
        FROM comments
        WHERE id = ? AND NOT deleted;
    """, (id_,)).fetchone()
    if record is None:
        return None
    return Comment(record["id"], record["text"], find_user_with_id(record["author_id"]))


def find_comments_left_for(article: Article) -> list[Comment]:
    """
    Получить список всех комментариев, оставленных к статье
    :param article: статья, для которой ищутся комментарии
    :return: список оставленных к статье комментариев, от старых к новым
    """
    records = get_connection().cursor().execute("""
        SELECT id, text, author_id
        FROM comments
        WHERE parent_article_id = ? AND NOT deleted;
    """, (article.id,)).fetchall()
    return [Comment(r["id"], r["text"], find_user_with_id(r["author_id"]))
            for r in records]


def find_comments_replied_at(comment: Comment) -> list[Comment]:
    """
    Получить список всех ответов к данному комментарию
    :param comment: комментарий, к которому ищутся ответы
    :return: список ответов к комментарию, от старых к новым
    """
    records = get_connection().cursor().execute("""
        SELECT id, text, author_id
        FROM comments
        WHERE parent_comment_id = ? AND NOT deleted;
    """, (comment.id,)).fetchall()
    return [Comment(r["id"], r["text"], find_user_with_id(r["author_id"]))
            for r in records]


def find_comments_left_by(user: User) -> list[Comment]:
    """
    Получить список комментариев и ответов к комментариям, оставленных данным пользователем
    :param user: пользователь, для которого ищутся комментарии
    :return: список оставленных пользователем комментариев и ответов, от старых к новым
    """
    records = get_connection().cursor().execute("""
        SELECT id, text
        FROM comments
        WHERE author_id = ? AND NOT deleted;
    """, (user.id,)).fetchall()
    return [Comment(r["id"], r["text"], user)
            for r in records]


def find_article_comment_was_left_for(comment: Comment) -> Article | None:
    """
    Найти статью, к которой был оставлен комментарий.
    В случае, если данный комментарий был оставлен как ответ на другой комментарий,
        находится исходная статья
    :param comment: комментарий, для которого ищется исходная статья
    :return: статья или None, если комментарий не был оставлен к какой-либо статье
    """
    record = get_connection().cursor().execute("""
        SELECT parent_article_id, parent_comment_id
        FROM comments
        WHERE id = ?;
    """, (comment.id,)).fetchone()
    if record is None:
        return None
    if record["parent_article_id"] is None:
        if record["parent_comment_id"] is not None:
            parent_comment = find_comment_with_id(record["parent_comment_id"])
            return find_article_comment_was_left_for(parent_comment)
        return None
    return find_article_with_id(record["parent_article_id"])


def _image_to_bytes(image: PILImage) -> bytes:
    byte_stream = io.BytesIO()
    image.save(byte_stream, "PNG")
    return byte_stream.getvalue()


def _image_from_bytes(image_bytes: bytes) -> PILImage:
    return PILImage.open(io.BytesIO(image_bytes))
