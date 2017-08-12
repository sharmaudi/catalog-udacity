from flask import Blueprint, flash, redirect, render_template
from flask_login import logout_user, login_required, current_user

user_blueprint = Blueprint('user', __name__, template_folder='templates')


@user_blueprint.route('/login', methods=['GET'])
def login():
    if current_user.is_authenticated:
        flash("You are already logged in", "info")
        return redirect("/")
    return render_template('user/login.html')


@user_blueprint.route("/logout")
@login_required
def logout():
    flash("You have been logged out.")
    logout_user()
    return redirect("/")
