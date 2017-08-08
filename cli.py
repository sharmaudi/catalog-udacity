from datetime import datetime

import click
from faker import Faker

import faker.providers.lorem as lorem
import faker.providers.internet as internet

from sqlalchemy_utils import database_exists, create_database

from app.app import create_app
from app.blueprints.catalog.models import Category, Item
from app.extensions import db

# Create an app context for the database connection.
app = create_app()
db.app = app

fake = Faker()

fake.add_provider(lorem)
fake.add_provider(internet)



def _bulk_insert(model, data, label):
    """
    Bulk insert data to a specific model and log it. This is much more
    efficient than adding 1 row at a time in a loop.

    :param model: Model being affected
    :type model: SQLAlchemy
    :param data: Data to be saved
    :type data: list
    :param label: Label for the output
    :type label: str
    :param skip_delete: Optionally delete previous records
    :type skip_delete: bool
    :return: None
    """
    with app.app_context():
        model.query.delete()

        db.session.commit()
        db.engine.execute(model.__table__.insert(), data)
        click.echo(f'Created {model.query.count()} {label}')

    return None



@click.group()
def cli():
    """ Run PostgreSQL related tasks. """
    pass


@click.command()
@click.option('--with-testdb/--no-with-testdb', default=False,
              help='Create a test db too?')
@click.option('--with-fake-data/--no-with-fake-data', default=True,
              help='Create fake data?')
def init(with_testdb, with_fake_data):
    """
    Initialize the database.

    :param with_fake_data: Create fake data
    :param with_testdb: Create a test database
    :return: None
    """
    uri = app.config['SQLALCHEMY_DATABASE_URI']
    print(f"Database uri is {uri}")
    if not database_exists(uri):
        create_database(uri)
    else:
        db.drop_all()
        db.create_all()

    if with_testdb:
        db_uri = '{0}_test'.format(app.config['SQLALCHEMY_DATABASE_URI'])
        if not database_exists(db_uri):
            create_database(db_uri)

    if with_fake_data:
        _seed_categories()
        _seed_items()
    return None


@click.command()
def seed_fake_data():
    _seed_categories()
    _seed_items()


def _seed_categories():
    categories = [
        'Soccer',
        'Baseball',
        'Basketball',
        'Frisbee',
        'Snowboarding',
        'Cricket',
        'Hockey',
        'Foosball'
    ]

    data = []

    for category in categories:
        fake_datetime = fake.date_time_between(
            start_date='-1y', end_date='now').strftime('%s')

        created_on = datetime.utcfromtimestamp(
            float(fake_datetime)).strftime('%Y-%m-%dT%H:%M:%S Z')

        data.append({
            'name': category,
            'description': fake.text(max_nb_chars=200, ext_word_list=None),
            'image': fake.image_url(width=None, height=None),
            'created_on': created_on
        })
    print(f"Creating categories: {data}")
    return _bulk_insert(Category, data, 'categories')


def _seed_items():
    data = []
    with app.app_context():
        categories = db.session.query(Category).all()

    for category in categories:

        for i in range(1, 10):

            created_on_fake = fake.date_time_between(
                start_date='-1y', end_date='now').strftime('%s')
            created_on = datetime.utcfromtimestamp(
                float(created_on_fake)).strftime('%Y-%m-%dT%H:%M:%S Z')

            data.append(
                {
                    'name': fake.word(),
                    'description': fake.text(max_nb_chars=400, ext_word_list=None),
                    'image': fake.image_url(width=None, height=None),
                    'created_on': created_on,
                    'category_id': category.id
                }
            )

    return _bulk_insert(Item, data, "items")

cli.add_command(init)
cli.add_command(seed_fake_data)

if __name__ == '__main__':
    cli()
