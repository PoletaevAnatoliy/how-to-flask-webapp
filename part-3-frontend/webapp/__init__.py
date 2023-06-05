import os.path

from flask import Flask, send_from_directory, url_for, redirect, render_template
from flask_login import LoginManager

from webapp.db import init_app
from webapp.db.accounting import register_user, find_user_with_email, find_user_with_id
from webapp.db.courses import find_all_courses, find_course_with_id, add_course


def create_app(config: dict = None):
    app = Flask("electro-guidebook")
    app.config.from_mapping(
        DATABASE=os.path.join(os.getcwd(), os.getenv("DATABASE", "database.db")),
        SECRET_KEY=os.getenv("SECRET_KEY", "dev")
    )
    if config is not None:
        app.config.update(config)
    init_app(app)
    login_manager = LoginManager()
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return find_user_with_id(user_id)

    @app.route("/favicon.ico")
    def favicon():
        return send_from_directory(os.path.join(app.static_folder, "img"),
                                   "favicon.png")

    @app.errorhandler(404)
    def not_found(e):
        return render_template("404.html", title="Страница не найдена")

    @app.route("/")
    def index():
        return redirect(url_for("courses.show_all_courses"))

    from webapp.accounting import accounting_bp

    app.register_blueprint(accounting_bp, url_prefix="/profile")

    from webapp.courses import courses_bp

    app.register_blueprint(courses_bp, url_prefix="/courses")

    return app
