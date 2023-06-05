from tests import BaseTestCase
from webapp import add_course, find_all_courses, register_user, find_user_with_email
from webapp.db.courses import find_courses_created_by, add_article, \
    find_articles_for, add_to_favored_courses, find_courses_favored_by, \
    left_comment_for, find_comments_left_for, find_comments_replied_at, \
    reply_at_comment, delete_comment, find_comments_left_by, \
    StudentsCannotReplyAtComments, StudentsCannotDeleteComments, \
    remove_from_favored_courses, StudentsCannotCreateArticles, CourseAlreadyExists, \
    edit_article


class TestCourses(BaseTestCase):

    def create_data(self):
        super().create_data()
        register_user("teacher", "a@mail.com", "12345")
        self.teacher = find_user_with_email("a@mail.com")
        register_user("student", "b@mail.com", "12345")
        self.student = find_user_with_email("b@mail.com")

    def test_creation(self):
        with self.app.app_context():
            self.create_data()
            course_title, course_description = "Python3 programming basics", "Мой первый курс по программированию на Python3"
            add_course(course_title, course_description, self.teacher)
            courses = find_all_courses()
            self.assertEqual(1, len(courses))
            course = courses[0]
            self.assertEqual(course_title, course.title)
            self.assertEqual(course_description, course.description)
            self.assertEqual(self.teacher, course.author)

    def test_course_title_duplication(self):
        with self.app.app_context():
            self.create_data()
            first_course_title, first_course_description = "Python3 programming basics", "Мой первый курс по программированию на Python3"
            second_course_title, second_course_description = "Python3 programming basics", "Мой второй курс по программированию на Python3"
            add_course(first_course_title, first_course_description, self.teacher)
            self.assertRaises(CourseAlreadyExists, add_course, second_course_title, second_course_description, self.student)

    def test_getting_created_by_user(self):
        with self.app.app_context():
            self.create_data()
            course_title, course_description = "Python3 programming basics", "Мой первый курс по программированию на Python3"
            add_course(course_title, course_description, self.teacher)
            courses = find_courses_created_by(self.teacher)
            self.assertEqual(1, len(courses))
            course = courses[0]
            self.assertEqual(course_title, course.title)
            self.assertEqual(course_description, course.description)
            self.assertEqual(self.teacher, course.author)

    def test_not_getting_not_created_by_user(self):
        with self.app.app_context():
            self.create_data()
            course_title, course_description = "Python3 programming basics", "Мой первый курс по программированию на Python3"
            add_course(course_title, course_description, self.teacher)
            self.assertEqual(0, len(find_courses_created_by(self.student)))

    def test_articles_creation(self):
        course_title, course_description = "First Course", "My First programming course"
        first_article_title, first_article_text = "First article", "Hello, "
        second_article_title, second_article_text = "Second article", "World!"
        with self.app.app_context():
            self.create_data()
            add_course(course_title, course_description, self.teacher)
            course = find_courses_created_by(self.teacher)[-1]
            add_article(first_article_title, first_article_text, course, self.teacher)
            add_article(second_article_title, second_article_text, course, self.teacher)
            articles = find_articles_for(course)
            self.assertEqual(2, len(articles))
            first_article, second_article = articles
            self.assertEqual(first_article_title, first_article.title)
            self.assertEqual(first_article_text, first_article.text)
            self.assertEqual(self.teacher, first_article.author)
            self.assertEqual(second_article_title, second_article.title)
            self.assertEqual(second_article_text, second_article.text)
            self.assertEqual(self.teacher, second_article.author)

    def test_article_editing(self):
        course_title, course_description = "First Course", "My First programming course"
        first_article_title, first_article_text = "First article", "Hello, "
        second_article_title, second_article_text = "Second article", "World!"
        second_article_new_title, second_article_new_text = "New title for the second article", "Weird New World!"
        with self.app.app_context():
            self.create_data()
            add_course(course_title, course_description, self.teacher)
            course = find_courses_created_by(self.teacher)[-1]
            add_article(first_article_title, first_article_text, course, self.teacher)
            add_article(second_article_title, second_article_text, course, self.teacher)
            first_article, second_article = find_articles_for(course)
            edit_article(second_article, second_article_new_title, second_article_new_text, self.teacher)
            first_article, second_article = find_articles_for(course)
            self.assertEqual(second_article_new_title, second_article.title)
            self.assertEqual(second_article_new_text, second_article.text)
            self.assertEqual(self.teacher, second_article.author)
            self.assertEqual(first_article_title, first_article.title)
            self.assertEqual(first_article_text, first_article.text)
            self.assertEqual(self.teacher, first_article.author)

    def test_courses_independency(self):
        first_course_title, first_course_description = "First Course", "Programming course"
        second_course_title, second_course_description = "Second Course", "Programming course"
        first_article_title, first_article_text = "First article", "Hello, "
        second_article_title, second_article_text = "Second article", "World!"
        with self.app.app_context():
            self.create_data()
            add_course(first_course_title, first_course_description, self.teacher)
            add_course(second_course_title, second_course_description, self.teacher)
            first_course, second_course = find_courses_created_by(self.teacher)
            add_article(first_article_title, first_article_text, first_course, self.teacher)
            add_article(second_article_title, second_article_text, second_course, self.teacher)
            first_course_articles = find_articles_for(first_course)
            self.assertEqual(1, len(first_course_articles))
            self.assertEqual(first_article_title, first_course_articles[0].title)
            self.assertEqual(first_article_text, first_course_articles[0].text)
            self.assertEqual(self.teacher, first_course_articles[0].author)
            second_course_articles = find_articles_for(second_course)
            self.assertEqual(1, len(second_course_articles), 1)
            self.assertEqual(second_article_title, second_course_articles[0].title)
            self.assertEqual(second_article_text, second_course_articles[0].text)
            self.assertEqual(self.teacher, second_course_articles[0].author)

    def test_student_cannot_create_article(self):
        course_title, course_description = "First Course", "My First programming course"
        article_title, article_text = "First article", "Hello, "
        with self.app.app_context():
            self.create_data()
            add_course(course_title, course_description, self.teacher)
            course = find_courses_created_by(self.teacher)[-1]
            self.assertRaises(StudentsCannotCreateArticles,
                              add_article, article_title, article_text, course, self.student)

    def test_favoring_courses_adding(self):
        first_course_title, first_course_description = "First Course", "My First programming course"
        second_course_title, second_course_description = "Second Course", "Other programming course"
        with self.app.app_context():
            self.create_data()
            add_course(first_course_title, first_course_description, self.teacher)
            add_course(second_course_title, second_course_description, self.teacher)
            first_course, second_course = find_courses_created_by(self.teacher)
            self.assertEqual(0, len(find_courses_favored_by(self.teacher)))
            self.assertEqual(0, len(find_courses_created_by(self.student)))
            add_to_favored_courses(first_course, self.student)
            self.assertEqual(0, len(find_courses_favored_by(self.teacher)))
            favored_courses = find_courses_favored_by(self.student)
            self.assertEqual(1, len(favored_courses))
            self.assertEqual(first_course, favored_courses[0])
            add_to_favored_courses(second_course, self.student)
            self.assertEqual(0, len(find_courses_favored_by(self.teacher)))
            favored_courses = find_courses_favored_by(self.student)
            self.assertEqual(2, len(favored_courses), 2)
            self.assertEqual(first_course, favored_courses[0])
            self.assertEqual(second_course, favored_courses[1])

    def test_favoring_courses_removing(self):
        first_course_title, first_course_description = "First Course", "My First programming course"
        second_course_title, second_course_description = "Second Course", "Other programming course"
        with self.app.app_context():
            self.create_data()
            add_course(first_course_title, first_course_description, self.teacher)
            add_course(second_course_title, second_course_description, self.teacher)
            first_course, second_course = find_courses_created_by(self.teacher)
            self.assertEqual(0, len(find_courses_favored_by(self.teacher)))
            self.assertEqual(0, len(find_courses_created_by(self.student)))
            add_to_favored_courses(first_course, self.student)
            add_to_favored_courses(second_course, self.student)
            self.assertEqual(0, len(find_courses_favored_by(self.teacher)))
            self.assertEqual(2, len(find_courses_favored_by(self.student)))
            remove_from_favored_courses(first_course, self.student)
            self.assertEqual(0, len(find_courses_favored_by(self.teacher)))
            self.assertEqual(1, len(find_courses_favored_by(self.student)))
            self.assertEqual(second_course, find_courses_favored_by(self.student)[0])

    def test_favoring_courses_removal_independency(self):
        first_course_title, first_course_description = "First Course", "My First programming course"
        second_course_title, second_course_description = "Second Course", "Other programming course"
        with self.app.app_context():
            self.create_data()
            add_course(first_course_title, first_course_description, self.teacher)
            add_course(second_course_title, second_course_description, self.teacher)
            first_course, second_course = find_courses_created_by(self.teacher)
            add_to_favored_courses(first_course, self.student)
            add_to_favored_courses(second_course, self.student)
            add_to_favored_courses(first_course, self.teacher)
            remove_from_favored_courses(first_course, self.student)
            self.assertEqual(1, len(find_courses_favored_by(self.teacher)))
            self.assertEqual(1, len(find_courses_favored_by(self.student)))
            self.assertEqual(second_course, find_courses_favored_by(self.student)[0])

    def test_commenting(self):
        course_title, course_description = "First course", "My first programming course"
        article_title, article_text = "Article #1", "Article about programming"
        first_comment_text, second_comment_text = "First comment", "Second comment"
        with self.app.app_context():
            self.create_data()
            add_course(course_title, course_description, self.teacher)
            course = find_courses_created_by(self.teacher)[0]
            add_article(article_title, article_text, course, self.teacher)
            article = find_articles_for(course)[0]
            left_comment_for(first_comment_text, article, self.student)
            left_comment_for(second_comment_text, article, self.teacher)
            first_comment, second_comment = find_comments_left_for(article)
            self.assertEqual(first_comment_text, first_comment.text)
            self.assertEqual(self.student, first_comment.author)
            self.assertEqual(second_comment_text, second_comment.text)
            self.assertEqual(self.teacher, second_comment.author)

    def test_commenting_independency(self):
        first_course_title, first_course_description = "First course", "My first programming course"
        second_course_title, second_course_description = "Second course", "My other programming course"
        first_article_title, first_article_text = "Article #1", "Article about programming"
        second_article_title, second_article_text = "Article #2", "Article about programming"
        third_article_title, third_article_text = "Article #3", "Article about programming"
        first_comment_text, second_comment_text, third_comment_text = "First comment", "Second comment", "Third comment"
        with self.app.app_context():
            self.create_data()
            add_course(first_course_title, first_course_description, self.teacher)
            add_course(second_course_title, second_course_description, self.teacher)
            first_course, second_course = find_courses_created_by(self.teacher)
            add_article(first_article_title, first_article_text, first_course, self.teacher)
            add_article(second_article_title, second_article_text, first_course, self.teacher)
            add_article(third_article_title, third_article_text, second_course, self.teacher)
            first_article, second_article = find_articles_for(first_course)
            third_article = find_articles_for(second_course)[0]
            left_comment_for(first_comment_text, first_article, self.student)
            left_comment_for(second_comment_text, second_article, self.teacher)
            left_comment_for(third_comment_text, third_article, self.student)
            first_comment = find_comments_left_for(first_article)[0]
            second_comment = find_comments_left_for(second_article)[0]
            third_comment = find_comments_left_for(third_article)[0]
            self.assertEqual(first_comment_text, first_comment.text)
            self.assertEqual(self.student, first_comment.author)
            self.assertEqual(second_comment_text, second_comment.text)
            self.assertEqual(self.teacher, second_comment.author)
            self.assertEqual(third_comment_text, third_comment.text)
            self.assertEqual(self.student, third_comment.author)

    def test_comments_replying(self):
        course_title, course_description = "First course", "My first programming course"
        article_title, article_text = "Article #1", "Article about programming"
        first_comment_text, second_comment_text = "First comment", "Second comment"
        reply_comment_text = "Reply at first comment"
        with self.app.app_context():
            self.create_data()
            add_course(course_title, course_description, self.teacher)
            course = find_courses_created_by(self.teacher)[0]
            add_article(article_title, article_text, course, self.teacher)
            article = find_articles_for(course)[0]
            left_comment_for(first_comment_text, article, self.student)
            left_comment_for(second_comment_text, article, self.teacher)
            first_comment, second_comment = find_comments_left_for(article)
            self.assertEqual(0, len(find_comments_replied_at(first_comment)))
            self.assertEqual(0, len(find_comments_replied_at(second_comment)))
            reply_at_comment(reply_comment_text, first_comment, self.teacher)
            self.assertEqual(1, len(find_comments_replied_at(first_comment)))
            reply_comment = find_comments_replied_at(first_comment)[0]
            self.assertEqual(reply_comment_text, reply_comment.text)
            self.assertEqual(self.teacher, reply_comment.author)
            self.assertEqual(0, len(find_comments_replied_at(second_comment)))

    def test_comments_deletion(self):
        course_title, course_description = "First course", "My first programming course"
        article_title, article_text = "Article #1", "Article about programming"
        first_comment_text, second_comment_text = "First comment", "Second comment"
        with self.app.app_context():
            self.create_data()
            add_course(course_title, course_description, self.teacher)
            course = find_courses_created_by(self.teacher)[0]
            add_article(article_title, article_text, course, self.teacher)
            article = find_articles_for(course)[0]
            left_comment_for(first_comment_text, article, self.student)
            left_comment_for(second_comment_text, article, self.teacher)
            comment_for_deletion = find_comments_left_for(article)[0]
            self.assertEqual(2, len(find_comments_left_for(article)))
            delete_comment(comment_for_deletion, self.teacher)
            self.assertEqual(1, len(find_comments_left_for(article)))
            remaining_comment = find_comments_left_for(article)[0]
            self.assertEqual(second_comment_text, remaining_comment.text)
            self.assertEqual(self.teacher, remaining_comment.author)

    def test_comments_replies_deletion(self):
        course_title, course_description = "First course", "My first programming course"
        article_title, article_text = "Article #1", "Article about programming"
        comment_text = "First comment"
        first_reply_text, second_reply_text = "First reply", "Second reply"
        with self.app.app_context():
            self.create_data()
            add_course(course_title, course_description, self.teacher)
            course = find_courses_created_by(self.teacher)[0]
            add_article(article_title, article_text, course, self.teacher)
            article = find_articles_for(course)[0]
            left_comment_for(comment_text, article, self.student)
            reply_at_comment(first_reply_text, find_comments_left_for(article)[0], self.teacher)
            reply_at_comment(first_reply_text, find_comments_left_for(article)[0], self.teacher)
            self.assertEqual(1, len(find_comments_left_for(article)))
            self.assertEqual(2, len(find_comments_left_by(self.teacher)))
            comment_for_deletion = find_comments_left_for(article)[0]
            delete_comment(comment_for_deletion, self.teacher)
            self.assertEqual(0, len(find_comments_left_for(article)))
            self.assertEqual(0, len(find_comments_left_by(self.teacher)))

    def test_students_cannot_reply_and_delete_comments(self):
        course_title, course_description = "First course", "My first programming course"
        article_title, article_text = "Article #1", "Article about programming"
        first_comment_text, second_comment_text = "First comment", "Second comment"
        reply_text = "Reply"
        with self.app.app_context():
            self.create_data()
            add_course(course_title, course_description, self.teacher)
            course = find_courses_created_by(self.teacher)[0]
            add_article(article_title, article_text, course, self.teacher)
            article = find_articles_for(course)[0]
            left_comment_for(first_comment_text, article, self.student)
            left_comment_for(second_comment_text, article, self.teacher)
            first_comment, second_comment = find_comments_left_for(article)
            self.assertRaises(StudentsCannotDeleteComments, delete_comment, first_comment, self.student)
            self.assertRaises(StudentsCannotDeleteComments, delete_comment, second_comment, self.student)
            self.assertRaises(StudentsCannotReplyAtComments, reply_at_comment, reply_text, first_comment, self.student)
            self.assertRaises(StudentsCannotReplyAtComments, reply_at_comment, reply_text, second_comment, self.student)

