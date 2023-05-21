from webapp.db import get_connection
from webapp.db.accounting import User, user_with_id


class Course:
    def __init__(self, id_: int, title: str, description: str, author: User):
        self.id = id_
        self.title = title
        self.description = description
        self.author = author


def add_course(title: str, description: str, author: User):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("""
        INSERT INTO courses (title, description, author_id)
        VALUES (?, ?, ?);
    """, (title, description, author.id))
    connection.commit()


def get_courses() -> list[Course]:
    cursor = get_connection().cursor()
    records = cursor.execute("""
        SELECT id, title, description, author_id
        FROM courses
        ORDER BY id;
    """).fetchall()
    return [Course(r["id"], r["title"],
                   r["description"], user_with_id(r["author_id"]))
            for r in records]


def course_with_id(id_: int) -> Course:
    cursor = get_connection().cursor()
    record = cursor.execute("""
        SELECT id, title, description, author_id
        FROM courses
        WHERE id = ?;
    """, (id_,)).fetchone()
    return Course(record["id"], record["title"],
                  record["description"], user_with_id(record["author_id"]))
