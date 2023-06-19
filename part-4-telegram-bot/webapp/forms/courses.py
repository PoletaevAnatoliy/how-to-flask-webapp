from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, MultipleFileField
from wtforms.validators import DataRequired, ValidationError

from webapp.utils import _is_image


class CourseForm(FlaskForm):
    title       = StringField("Название курса", validators=[DataRequired()])
    description = StringField("Описание курса", validators=[DataRequired()])


class ArticleForm(FlaskForm):
    title  = StringField("Название статьи", validators=[DataRequired()])
    text   = TextAreaField("Текст статьи (абзацы отделяются пустыми строками)",
                          validators=[DataRequired()])
    images = MultipleFileField("Прикрепите изображения")

    def validate_images(form, field):
        formats = {"jpg", "jpeg", "png"}
        for image in field.data:
            if not _is_image(image):
                continue
            if image.content_type.split("/")[-1] not in formats:
                formats_message = ', '.join(f".{f}" for f in formats)
                raise ValidationError(f"Допустимые форматы файлов: {formats_message}")


class CommentForm(FlaskForm):
    text = StringField("Ваш комментарий", validators=[DataRequired()])
