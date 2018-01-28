from datetime import datetime
from flask import render_template, session, redirect, url_for
from . import main
from .forms import NameForm
from .. import db
from .. models import User


@main.route('/', methods=['GET', 'POST'])
def index():
    form = NameForm()
    if form.validate_on_submit():
        # old_name = session.get('name')
        # if old_name != None and old_name != form.name.data:
        #     flash('looks like you have chenged your name')
        # session['name'] = form.name.data
        # form.name.data = ""
        user = User.query.filter_by(username=form.username.data).first()
        if user is None:
            user = User(email=form.emial.data, username=form.username.data, password=form.password.data, role_id=1)
            db.session.add(user)
            session['known'] = False
            # if app.config['FlASY_ADMIN']:
            # send_email('zhaowh3613@outlook.com', 'new user '+user.name, 'mail/new_user', user=user)
        else:
            session['known'] = True
        session['username'] = form.username.data
        form.username.data = ''
        return redirect(url_for('.index'))
    return render_template('index.html', form=form, username=session.get('username'), known=session.get('known'), current_time=datetime.utcnow())
