from datetime import datetime, timezone, timedelta
from flask import render_template, flash, redirect, url_for
from flask_login import current_user, login_required
import sqlalchemy as sa
from app import database
from app.main import bp
from app.main.forms import NoteForm
from app.models import Note


@bp.route("/", methods=["GET", "POST"])
@bp.route("/index", methods=["GET", "POST"])
@login_required
def index():
    form = NoteForm()
    if form.validate_on_submit():
        note = Note(body=form.note.data, author=current_user)
        database.session.add(note)
        database.session.commit()
        flash("You did it!")
        return redirect(url_for("main.index"))
    # notes = current_user.notes
    notes = Note.query.filter_by(author=current_user).order_by(sa.desc("timestamp")).all()
    tz = timezone(timedelta(hours=3))
    return render_template("index.html", title="Main", form=form, notes=notes, tz=tz)
