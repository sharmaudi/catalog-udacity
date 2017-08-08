from flask import Blueprint, request, flash, redirect, render_template
from flask_login import logout_user

from app.blueprints.user.decorators import anonymous_required

user_blueprint = Blueprint('user', __name__, template_folder='templates')


@user_blueprint.route('/login', methods=['GET'])
@anonymous_required()
def login():
    return render_template('user/login.html')


@user_blueprint.route("/logout")
def logout():
    flash("You have been logged out.")
    logout_user()
    return redirect("/")
