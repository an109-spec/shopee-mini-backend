import click
from flask.cli import with_appcontext

from app.extensions import db


@click.command("init-db")
@click.option("--drop", is_flag=True, help="Drop all existing tables before create_all.")
@with_appcontext
def init_db_command(drop: bool) -> None:
    """Initialize database tables from SQLAlchemy models."""
    # ensure all models are imported so metadata is complete
    from app import models  # noqa: F401

    if drop:
        db.drop_all()
        click.echo("Dropped all tables.")

    db.create_all()
    click.echo("Database tables created successfully.")


def register_cli(app) -> None:
    app.cli.add_command(init_db_command)