import datetime
import os

import click
import pytz as pytz
import requests
from flask import Flask, render_template, session, flash
from flask_breadcrumbs import Breadcrumbs
from flask_dance.consumer import oauth_authorized
from flask_dance.consumer.backend.sqla import SQLAlchemyBackend
from flask_dance.contrib.facebook import make_facebook_blueprint
from flask_dance.contrib.github import make_github_blueprint
from flask_dance.contrib.google import make_google_blueprint
from flask_login import current_user, login_user
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy_utils import database_exists, create_database
from werkzeug.contrib.fixers import ProxyFix

from app.blueprints.catalog.views import catalog
from app.blueprints.user.models import User, OAuth
from app.blueprints.user.views import user_blueprint
from app.extensions import login_manager, csrf, debug_toolbar, db


def create_app(settings_override=None):
    """
    Creates a flask application using the App Factory pattern
    :param settings_override: Override default settings.
    :return: Flask app
    """
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object('config.settings')
    app.config.from_pyfile('settings.py', silent=True)

    app.config['TESTING'] = False

    print(app.config)
    error_templates(app)
    middleware(app)
    extensions(app)
    app.register_blueprint(catalog)
    app.register_blueprint(user_blueprint)
    init_oauth_providers(app)
    template_processors(app)
    authentication(app, User)
    register_commands(app)

    return app


def error_templates(app):
    """
    Register 0 or more custom error pages (mutates the app passed in).

    :param app: Flask application instance
    :return: None
    """

    def render_status(status):
        """
         Render a custom template for a specific status.
           Source: http://stackoverflow.com/a/30108946

         :param status: Status as a written name
         :type status: str
         :return: None
         """
        # Get the status code from the status, default to a 500 so that we
        # catch all types of errors and treat them as a 500.
        code = getattr(status, 'code', 500)
        return render_template('errors/{0}.html'.format(code)), code

    for error in [404, 500]:
        app.errorhandler(error)(render_status)
    return None


def middleware(app):
    """
    Register 0 or more middleware (mutates the app passed in).

    :param app: Flask application instance
    :return: None
    """
    # Swap request.remote_addr with the real IP address even if behind a proxy.
    app.wsgi_app = ProxyFix(app.wsgi_app)
    return None


def extensions(app):
    """
    Register 0 or more extensions (mutates the app passed in).

    :param app: Flask application instance
    :return: None
    """
    debug_toolbar.init_app(app)
    csrf.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    Breadcrumbs(app=app)
    return None


def authentication(app, user_model):
    """
    Initialize the Flask-Login extension (mutates the app passed in).

    :param app: Flask application instance
    :param user_model: Model that contains the authentication information
    :type user_model: SQLAlchemy model
    :return: None
    """
    login_manager.login_view = 'user.login'

    @app.before_request
    def make_session_permanent():
        session.permanent = True
        app.permanent_session_lifetime = datetime.timedelta(minutes=15)

    @login_manager.user_loader
    def load_user(uid):
        return User.query.get(int(uid))


def template_processors(app):
    """
    Register 0 or more custom template processors (mutates the app passed in).

    :param app: Flask application instance
    :return: App jinja environment
    """
    app.jinja_env.globals.update(current_year=datetime.datetime.now(pytz.utc).year)
    return app.jinja_env


def register_commands(app):
    @app.cli.command()
    @click.option('--with-testdb/--no-with-testdb', default=False,
                  help='Create a test db too?')
    def initdb(with_testdb):
        """Initialize the database."""
        click.echo('Initializing db')
        db.drop_all()
        db.create_all()

        if with_testdb:
            db_uri = '{0}_test'.format(app.config['SQLALCHEMY_DATABASE_URI'])

            if not database_exists(db_uri):
                create_database(db_uri)

        return None


def init_oauth_providers(app):
    # OAuth blueprints
    if app.config['OAUTHLIB_INSECURE_TRANSPORT']:
        os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = "1"
        os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = "1"

    if 'GOOGLE' in app.config.get('OAUTH_CONFIG'):
        register_google_blueprint(app)

    if 'FACEBOOK' in app.config.get('OAUTH_CONFIG'):
        register_facebook_blueprint(app)

    if 'GITHUB' in app.config.get('OAUTH_CONFIG'):
        register_github_blueprint(app)


def register_google_blueprint(app):
    # Google
    client_id = app.config.get('OAUTH_CONFIG')['GOOGLE']['client_id']
    client_secret = app.config.get('OAUTH_CONFIG')['GOOGLE']['client_secret']
    google_blueprint = make_google_blueprint(
        client_id=client_id,
        client_secret=client_secret,
        scope=["openid", "profile", "email"]
    )
    google_blueprint.backend = SQLAlchemyBackend(OAuth, db.session, user=current_user)
    app.register_blueprint(google_blueprint, url_prefix="/login")

    # create/login local user on successful OAuth login
    @oauth_authorized.connect_via(google_blueprint)
    def google_logged_in(blueprint, token):
        if not token:
            flash("Failed to log in with {name}".format(name=blueprint.name))
            return
        # figure out who the user is
        resp = blueprint.session.get("/oauth2/v2/userinfo")
        if resp.ok:
            username = resp.json()["email"]
            query = User.query.filter_by(username=username)
            try:
                user = query.one()
            except NoResultFound:
                # create a user
                user = User()
                user.username = username
                user.save()
            login_user(user)
            flash("Successfully signed in with Google", "success")
        else:
            msg = "Failed to fetch user info from {name}".format(name=blueprint.name)
            flash(msg, category="error")


def register_facebook_blueprint(app):
    # Facebook
    client_id = app.config.get('OAUTH_CONFIG')['FACEBOOK']['client_id']
    client_secret = app.config.get('OAUTH_CONFIG')['FACEBOOK']['client_secret']

    facebook_blueprint = make_facebook_blueprint(
        client_id=client_id,
        client_secret=client_secret,
        scope=["public_profile", "email"]
    )
    facebook_blueprint.backend = SQLAlchemyBackend(OAuth, db.session, user=current_user)
    app_token = get_facebook_app_token(app)
    if app_token:
        app.register_blueprint(facebook_blueprint, url_prefix="/login")
    else:
        print("Facebook app token not found in config. Facebook blueprint not configured.")

    @oauth_authorized.connect_via(facebook_blueprint)
    def facebook_logged_in(blueprint, token):
        if not token:
            flash("Failed to log in with {name}".format(name=blueprint.name))
            return
        # figure out who the user is
        resp = blueprint.session.get("/me?fields=email,name")
        if resp.ok:
            print(f"Response from facebook: {resp.json()}")
            username = resp.json()["email"]
            query = User.query.filter_by(username=username)
            try:
                user = query.one()
            except NoResultFound:
                # create a user
                user = User()
                user.username = username
                user.save()
            login_user(user)
            flash("Successfully signed in with Facebook", "success")
        else:
            print(resp.text)
            msg = "Failed to fetch user info from {name}".format(name=blueprint.name)
            flash(msg, category="error")


def register_github_blueprint(app):
    # Facebook
    client_id = app.config.get('OAUTH_CONFIG')['GITHUB']['client_id']
    client_secret = app.config.get('OAUTH_CONFIG')['GITHUB']['client_secret']

    github_blueprint = make_github_blueprint(
        client_id=client_id,
        client_secret=client_secret,
        scope=["public_profile", "email"]
    )
    github_blueprint.backend = SQLAlchemyBackend(OAuth, db.session, user=current_user)
    app.register_blueprint(github_blueprint, url_prefix="/login")

    @oauth_authorized.connect_via(github_blueprint)
    def github_logged_in(blueprint, token):
        if not token:
            flash("Failed to log in with {name}".format(name=blueprint.name))
            return
        # figure out who the user is
        resp = blueprint.session.get("/user")
        if resp.ok:
            print(f"Response from github: {resp.json()}")
            username = resp.json()["login"]
            query = User.query.filter_by(username=username)
            try:
                user = query.one()
            except NoResultFound:
                # create a user
                user = User()
                user.username = username
                user.save()
            login_user(user)
            flash("Successfully signed in with Github", "success")
        else:
            print(resp.text)
            msg = "Failed to fetch user info from {name}".format(name=blueprint.name)
            flash(msg, category="error")


def get_facebook_app_token(app):
    if "FACEBOOK_APP_TOKEN" in app.config and app.config["FACEBOOK_APP_TOKEN"]:
        app_token = app.config["FACEBOOK_APP_TOKEN"]
    else:
        client_id = app.config.get('OAUTH_CONFIG')['FACEBOOK']['client_id']
        client_secret = app.config.get('OAUTH_CONFIG')['FACEBOOK']['client_secret']
        app_access_token_response = requests.get(f"https://graph.facebook.com/oauth/access_token?client_id={client_id}&"
                                                 f"client_secret={client_secret}&grant_type=client_credentials")
        if app_access_token_response.ok:
            app_token = app_access_token_response.json()['access_token']
            app.config["FACEBOOK_APP_TOKEN"] = app_token
        else:
            app_token = None

    return app_token

