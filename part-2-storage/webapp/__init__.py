import os.path

from flask import Flask, render_template, send_from_directory, request, redirect, \
    url_for
from flask_login import LoginManager, current_user, logout_user, login_user, \
    login_required

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

    @app.route("/")
    @app.route("/index")
    def index():
        return render_template("index.html", courses=find_all_courses())

    @app.route("/logout")
    @login_required
    def logout():
        app.logger.debug("User %s logged out", current_user.login)
        logout_user()
        return redirect(url_for("index"))

    @app.route("/login", methods=("GET", "POST"))
    def login():
        if request.method == "GET":
            return render_template("login.html")
        data = request.form.to_dict()
        user = find_user_with_email(data["email"])
        if user.check_password(data["password"]):
            app.logger.debug("User %s logged in", user.login)
            login_user(user)
            return redirect(url_for("index"))
        return render_template("login.html")

    @app.route("/register", methods=("GET", "POST"))
    def register():
        if request.method == "GET":
            return render_template("register.html")
        data = request.form.to_dict()
        register_user(data["login"], data["email"], data["password"])
        app.logger.debug("User %s registred", data["login"])
        user = find_user_with_email(data["email"])
        login_user(user)
        return redirect(url_for("index"))

    @app.route("/profile")
    def profile():
        return render_template("profile.html")

    @app.route("/course", methods=("GET", "POST"))
    @login_required
    def create_course():
        if request.method == "GET":
            return render_template("create_course.html")
        form = request.form.to_dict()
        add_course(form["title"], form["description"], current_user)
        return redirect(url_for("index"))

    @app.route("/course/<int:course_id>")
    def course(course_id):
        return render_template("course.html", course=find_course_with_id(course_id))

    @app.route("/favicon.ico")
    def favicon():
        return send_from_directory(os.path.join(app.static_folder, "img"),
                                   "favicon.png")

    return app
