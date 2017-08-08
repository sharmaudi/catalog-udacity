from flask_dance.consumer.backend.sqla import OAuthConsumerMixin
from flask_login import UserMixin

from app.extensions import db
from app.mixins.sqlalchemy_resource_mixin import ResourceMixin


class User(db.Model, ResourceMixin, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(256), unique=True)


class OAuth(OAuthConsumerMixin, db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    user = db.relationship(User)
