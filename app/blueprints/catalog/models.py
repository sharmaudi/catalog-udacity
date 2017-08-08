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

    def get_items(self):
        return Item.query.join(Category).filter(Category.id == self.id)


class Item(db.Model, ResourceMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256))
    description = db.Column(db.String())
    image = db.Column(db.String())
    category_id = db.Column(db.Integer, db.ForeignKey(Category.id))
    category = db.relationship(Category)

    @classmethod
    def get_item(cls, category_name, item_name):
        return Item.query.join(Category).\
            filter(func.lower(Category.name) == func.lower(category_name)).\
            filter(func.lower(Item.name) == func.lower(item_name)).one()
