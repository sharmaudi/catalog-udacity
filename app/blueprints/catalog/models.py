from sqlalchemy import func

from app.extensions import db
from app.mixins.sqlalchemy_resource_mixin import ResourceMixin


class Category(db.Model, ResourceMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), unique=True)
    description = db.Column(db.String(), unique=False)
    image = db.Column(db.String())

    @classmethod
    def category_details(cls, name):
        return Category.query.filter(func.lower(Category.name) == func.lower(name)).one()

    @classmethod
    def get_categories_as_list(cls):
        return [category[0] for category in Category.query.with_entities(Category.name).all()]

    @classmethod
    def get_categories_as_dict(cls):
        return {category[0]: category[1] for category in Category.query.with_entities(Category.id, Category.name).all()}

    def get_items(self):
        return Item.query.join(Category).filter(Category.id == self.id)


class Item(db.Model, ResourceMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256))
    description = db.Column(db.String())
    image = db.Column(db.String())
    category_id = db.Column(db.Integer, db.ForeignKey(Category.id))
    category = db.relationship(Category)

    def __init__(self, **kwargs):
        # Call Flask-SQLAlchemy's constructor.
        super(Item, self).__init__(**kwargs)

    @classmethod
    def get_item(cls, category_name, item_name):
        return Item.query.join(Category). \
            filter(func.lower(Category.name) == func.lower(category_name)). \
            filter(func.lower(Item.name) == func.lower(item_name)).one()

