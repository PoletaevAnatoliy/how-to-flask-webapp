import base64
import io
from collections import OrderedDict
from functools import partial

from flask import Blueprint, request, render_template, redirect, url_for, \
    current_app, abort
from flask_login import login_required, current_user
from PIL import Image as PILImage

import webapp.db.courses as db
from webapp.forms.courses import CourseForm, ArticleForm, CommentForm
from webapp.models.courses import Article, Comment, Image
from webapp.utils import _is_image

courses_bp = Blueprint("courses", __name__)


@courses_bp.route("/")
def show_all_courses():
    if current_user.is_authenticated:
        favored_courses = db.find_courses_favored_by(current_user)
        other_courses = [c for c in db.find_all_courses() if c not in favored_courses]
        courses = favored_courses + other_courses
    else:
        courses = db.find_all_courses()
        favored_courses = []
    return render_template("all_courses.html", courses=courses,
                           favored_courses=favored_courses)


@courses_bp.route("/course-<int:course_id>/favour", methods=("POST",))
@login_required
def add_to_favored_courses(course_id: int):
    course = db.find_course_with_id(course_id)
    if course is None:
        abort(404)
    db.add_to_favored_courses(course, current_user)
    return redirect(url_for(".show_all_courses"))


@courses_bp.route("/course-<int:course_id>/unfavor", methods=("POST",))
@login_required
def remove_from_favored_courses(course_id: int):
    course = db.find_course_with_id(course_id)
    if course is None:
        abort(404)
    db.remove_from_favored_courses(course, current_user)
    return redirect(url_for(".show_all_courses"))


@courses_bp.route("/new-course", methods=("GET", "POST"))
@login_required
def create_course():
    form = CourseForm()
    render_template_ = partial(render_template, "create_course.html",
                               form=form, title="Новый курс")
    if request.method == "GET":
        return render_template_()
    if not form.validate_on_submit():
        errors = ['; '.join(map(str, e)) for e in form.errors.values()]
        return render_template_(errors=errors)
    try:
        db.add_course(form.title.data, form.description.data, current_user)
    except db.CourseAlreadyExists:
        errors = [f"Курс «{form.title.data}» уже существует"]
        return render_template_(errors=errors)
    current_app.logger.debug("Course '%s' created by user %s", form.title.data, current_user.login)
    return render_template("all_courses.html",
                           messages=[f"Курс «{form.title.data}» успешно создан"],
                           courses=db.find_all_courses())


@courses_bp.route("/course-<int:course_id>")
def show_course(course_id: int):
    course = db.find_course_with_id(course_id)
    if course is None:
        abort(404)
    articles = db.find_articles_for(course)
    return render_template("course.html", title=course.title,
                           course=course, articles=articles)


@courses_bp.route("/course-<int:course_id>/new-article")
@login_required
def create_article(course_id: int):
    course = db.find_course_with_id(course_id)
    if course is None:
        abort(404)
    try:
        db.add_article("", "", course, current_user)
    except db.StudentsCannotCreateArticles:
        abort(404)
    created_article = db.find_articles_for(course)[-1]
    return redirect(url_for(".edit_article",
                            course_id=course_id,
                            article_id=created_article.id))


@courses_bp.route("/course-<int:course_id>/article-<int:article_id>/edit", methods=("GET", "POST"))
@login_required
def edit_article(course_id: int, article_id: int):
    course = db.find_course_with_id(course_id)
    article = db.find_article_with_id(article_id)
    if course is None or article is None or current_user != article.author:
        abort(404)
    form = ArticleForm()
    if not form.validate_on_submit():
        form.title.data = article.title
        form.text.data = article.text
        errors = ['; '.join(map(str, e)) for e in form.errors.values()]
        return render_template("edit_article.html", form=form, errors=errors)
    try:
        images = [_load_image(storage) for storage in form.images.data
                  if _is_image(storage)]
        for image in images:
            db.add_image(image, article, current_user)
        db.edit_article(article, form.title.data,
                        form.text.data.replace('\r\n', '\n'), current_user)
    except db.StudentsCannotEditArticles:
        abort(404)
    current_app.logger.debug("Article '%s' edited", article.title)
    return redirect(url_for(".show_article", course_id=course.id, article_id=article_id))


@courses_bp.route("/course-<int:course_id>/article-<int:article_id>")
def show_article(course_id: int, article_id: int):
    course = db.find_course_with_id(course_id)
    article = db.find_article_with_id(article_id)
    if course is None or article is None:
        abort(404)
    comments = _collect_comments_for(article)
    images = [_dump_image(image) for image in db.find_images_in(article)]
    form = CommentForm()
    return render_template("article.html", title=article.title, form=form,
                           course=course, article=article, comments=comments,
                           images=images)


@courses_bp.route("/course-<int:course_id>/article-<int:article_id>/new-comment",
                  methods=("POST",))
@login_required
def create_comment(course_id: int, article_id: int):
    course = db.find_course_with_id(course_id)
    article = db.find_article_with_id(article_id)
    if course is None or article is None:
        abort(404)
    form = CommentForm()
    if not form.validate_on_submit():
        errors = ['; '.join(map(str, e)) for e in form.errors.values()]
        return render_template("article.html", title=article.title,
                               course=course, article=article, errors=errors,
                               comments=_collect_comments_for(article))
    db.left_comment_for(form.text.data, article, current_user)
    return redirect(url_for(".show_article", article_id=article.id, course_id=course.id))


@courses_bp.route("/course-<int:course_id>/article-<int:article_id>/comment-<int:comment_id>/reply",
                  methods=("POST",))
@login_required
def reply_to_comment(course_id: int, article_id: int, comment_id: int):
    course = db.find_course_with_id(course_id)
    article = db.find_article_with_id(article_id)
    comment = db.find_comment_with_id(comment_id)
    if course is None or article is None or comment is None:
        abort(404)
    form = CommentForm()
    if not form.validate_on_submit():
        errors = ['; '.join(map(str, e)) for e in form.errors.values()]
        return render_template("article.html", title=article.title,
                               course=course, article=article, errors=errors,
                               comments=_collect_comments_for(article))
    try:
        db.reply_at_comment(form.text.data, comment, current_user)
    except db.StudentsCannotReplyAtComments:
        errors = ["Только преподаватель может отвечать на комментарии!"]
        return render_template("article.html", title=article.title,
                               course=course, article=article, errors=errors,
                               comments=_collect_comments_for(article))
    return redirect(url_for(".show_article", article_id=article.id, course_id=course.id))


@courses_bp.route("/course-<int:course_id>/article-<int:article_id>/comment-<int:comment_id>/delete",
                  methods=("POST",))
@login_required
def delete_comment(course_id: int, article_id: int, comment_id: int):
    course = db.find_course_with_id(course_id)
    article = db.find_article_with_id(article_id)
    comment = db.find_comment_with_id(comment_id)
    if course is None or article is None or comment is None:
        abort(404)
    try:
        db.delete_comment(comment, current_user)
    except db.StudentsCannotDeleteComments:
        errors = ["Только преподаватель может удалять на комментарии!"]
        return render_template("article.html", title=article.title,
                               course=course, article=article, errors=errors,
                               comments=_collect_comments_for(article))
    return redirect(url_for(".show_article", article_id=article.id, course_id=course.id))


@courses_bp.route("/comment-<int:comment_id>")
def link_to_comment(comment_id: int):
    comment = db.find_comment_with_id(comment_id)
    if comment is None:
        abort(404)
    article = db.find_article_comment_was_left_for(comment)
    if article is None:
        abort(404)
    course = db.find_course_for_article(article)
    if course is None:
        abort(404)
    return redirect(url_for(".show_article", course_id=course.id, article_id=article.id,
                            _anchor=f"comment-{comment_id}"))


def _collect_comments_for(article: Article) -> OrderedDict[Comment, list[Comment]]:
    result = OrderedDict()
    for comment in db.find_comments_left_for(article):
        result[comment] = db.find_comments_replied_at(comment)
    return result


def _load_image(image_form_data) -> PILImage:
    image_bytes = image_form_data.read()
    return PILImage.open(io.BytesIO(image_bytes))


def _dump_image(image: Image):
    buffer = io.BytesIO()
    image.image.save(buffer, "PNG")
    return base64.b64encode(buffer.getvalue()).decode("utf-8")
