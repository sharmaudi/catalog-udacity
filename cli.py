import click

from sqlalchemy_utils import database_exists, create_database

from app.app import create_app
from app.blueprints.catalog.models import Category, Item
from app.extensions import db
import json
import datetime

# Create an app context for the database connection.
app = create_app()
db.app = app


@click.group()
def cli():
    """ Run PostgreSQL related tasks. """
    pass


@click.command()
@click.option('--with-testdb/--no-with-testdb', default=False,
              help='Create a test db too?')
@click.option('--with-data/--no-with-data', default=True,
              help='Seed data?')
def init(with_testdb, with_data):
    """
    Initialize the database.

    :param with_data:
    :param with_testdb: Create a test database
    :return: None
    """
    uri = app.config['SQLALCHEMY_DATABASE_URI']
    print(f"Database uri is {uri}")
    if not database_exists(uri):
        create_database(uri)
        db.create_all()
    else:
        db.drop_all()
        db.create_all()

    if with_testdb:
        db_uri = '{0}_test'.format(app.config['SQLALCHEMY_DATABASE_URI'])
        if not database_exists(db_uri):
            create_database(db_uri)

    if with_data:
        _seed_catalog()
    return None


@click.command()
def seed_data():
    _seed_catalog()


# noinspection PyTypeChecker
def _seed_catalog():
    with open('catalog.json') as catalog_file:
        catalog = json.load(catalog_file)

    categories = []
    items = []
    for category in catalog['Catalog']:
        categories.append(Category(
            id=category['id'],
            name=category['name'],
            description=category['description'],
            image=category['image'],
            created_on=_get_date(category['created_on']),
            updated_on=_get_date(category['updated_on'])
        ))

        for item in category['items']:
            items.append(Item(
                name=item['name'],
                description=item['description'],
                category_id=category['id'],
                image=item['image'],
                created_on=_get_date(category['created_on']),
                updated_on=_get_date(category['updated_on'])
            ))

    print(f"Creating {len(categories)} categories")
    _bulk_save_objects(Category, categories)
    _bulk_save_objects(Item, items)


def _get_date(string):
    return datetime.datetime.strptime(string, "%a, %d %b %Y %H:%M:%S GMT")


def _bulk_save_objects(model, objects):
    with app.app_context():
        model.query.delete()
        db.session.commit()
        db.session.bulk_save_objects(objects)
        db.session.commit()
        print(f"Inserted {model.query.count()} objects")

cli.add_command(init)
cli.add_command(seed_data)

if __name__ == '__main__':
    cli()
