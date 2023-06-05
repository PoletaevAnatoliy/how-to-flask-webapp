import os.path

from PIL import Image as PILImage

from tests import BaseTestCase
from webapp import register_user, find_user_with_email, add_course
from webapp.db.courses import find_courses_created_by, add_article, find_articles_for, add_image, find_images_in


class ImagesTest(BaseTestCase):

    def create_data(self):
        super().create_data()
        self.images_path = os.path.join(self.app.root_path, "tests", "resources")
        register_user("teacher", "teacher@mail.com", "qwerty123")
        self.teacher = find_user_with_email("teacher@mail.com")
        register_user("student", "student@mail.com", "qwerty123")
        self.student = find_user_with_email("student@mail.com")
        course_title, course_description = "First course", "My first programming course"
        first_article_title, first_article_text = "Article #1", "Article about programming"
        second_article_title, second_article_text = "Article #2", "Article about programming"
        add_course(course_title, course_description, self.teacher)
        self.course = find_courses_created_by(self.teacher)[0]
        add_article(first_article_title, first_article_text, self.course, self.teacher)
        add_article(second_article_title, second_article_text, self.course, self.teacher)
        self.first_article, self.second_article = find_articles_for(self.course)
        self.first_image = PILImage.open(os.path.join(self.images_path, "image-1.jpg"))
        self.second_image = PILImage.open(os.path.join(self.images_path, "image-2.png"))

    def test_images_adding(self):
        with self.app.app_context():
            self.create_data()
            self.assertEqual(0, len(find_images_in(self.first_article)))
            self.assertEqual(0, len(find_images_in(self.second_article)))
            add_image(self.first_image, self.first_article, self.teacher)
            add_image(self.second_image, self.second_article, self.teacher)
            self.assertEqual(1, len(find_images_in(self.first_article)))
            self.assertEqual(1, len(find_images_in(self.second_article)))
            first_saved_image = find_images_in(self.first_article)[0]
            second_saved_image = find_images_in(self.second_article)[0]
            self.assertTrue(self.first_image.getdata(), first_saved_image._to_rgb())
            self.assertTrue(self.second_image.getdata(), second_saved_image._to_rgb())
