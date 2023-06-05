import os
import sqlite3

import click
from flask import Flask, current_app, g


def init_app(app: Flask):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)


def init_db():
    db = get_connection()
    with current_app.open_resource("db-schema.sql") as f:
        db.executescript(f.read().decode("utf-8"))


def get_connection():
    if "db" not in g:
        db_name = current_app.config['DATABASE']
        db_address = os.path.join(os.getcwd(), db_name) if db_name != ":memory:" else db_name
        current_app.logger.debug("Connecting to the database %s", db_name)
        g.db = sqlite3.connect(db_address)
        g.db.row_factory = sqlite3.Row
    return g.db


def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        current_app.logger.debug("Disconnecting from the database")
        db.close()


@click.command("init-db")
def init_db_command():
    init_db()
    click.echo("Initialized database")



