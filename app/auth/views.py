from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user
import sqlalchemy as sa
from app import database
from app.auth import bp
from app.auth.forms import LoginForm, RegistrationForm
from app.models import User
from urllib.parse import urlsplit
from datetime import timedelta


@bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        flash("You can't see login page when you are authenticated already")
        return redirect(url_for("main.index"))
    form = LoginForm()
    if form.validate_on_submit():
        user = database.session.scalar(
            sa.select(User).where(User.name == form.username.data)
        )
        if user is None or not user.check_password(form.passwd.data):
            flash("Invalid username or password")
            return redirect(url_for("auth.login"))
        login_user(user, remember=form.remember_me.data, duration=timedelta(hours=24))
        next_page = request.args.get("next")
        if next_page is None or urlsplit(next_page).netloc != "":
            next_page = url_for("main.index")
        return redirect(next_page)
    return render_template("auth/login.html", title="Authentication", form=form)


@bp.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("main.index"))


@bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        flash("You can't see registration page when you are authenticated already")
        return redirect(url_for("main.index"))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(name=form.username.data)
        user.email = form.email.data
        user.set_password(form.passwd.data)
        database.session.add(user)
        database.session.commit()
        flash("Registration complete!")
        return redirect(url_for("auth.login"))
    return render_template("auth/register.html", title="Registration", form=form)
