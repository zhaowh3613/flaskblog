from flask import Flask, request, render_template, redirect, session, url_for, flash
from flask_script import Manager
from flask_bootstrap import Bootstrap
from flask_wtf import Form
from wtforms import StringField, SubmitField
from wtforms.validators import Required
from flask_sqlalchemy import SQLAlchemy
from flask_moment import Moment
from datetime import datetime
from flask_migrate import Migrate, MigrateCommand
from flask_mail import Mail, Message
from threading import Thread

import os


basedir = os.path.abspath(os.path.dirname(__file__))
print('basedir ' + basedir)
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] =\
    'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
db = SQLAlchemy(app)

app.config['SECRET_KEY'] = '123456789'
app.config.update(dict(
    DEBUG=True,
    MAIL_SERVER='smtp.163.com',
    MAIL_PORT=25,
    MAIL_USE_TLS=True,
    MAIL_USE_SSL=False,
    MAIL_USERNAME=os.environ.get('MAIL_USERNAME'),
    MAIL_PASSWORD=os.environ.get('MAIL_PASSWORD'),
))
app.config['FLASKY_MAIL_SUBJECT_PREFIX'] = '[Flasky]'
app.config['FLASKY_MAIL_SENDER'] = os.environ.get('MAIL_USERNAME')
app.config['FLASKY_ADMIN'] = os.environ.get('MAIL_USERNAME')


mail = Mail(app)
manager = Manager(app)
bootstrap = Bootstrap(app)
moment = Moment(app)

migrate = Migrate(app, db)


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(to, subject, template, **kwarqs):

    # print(os.environ.get('MAIL_USERNAME'))
    msg = Message(app.config['FLASKY_MAIL_SUBJECT_PREFIX']+subject, sender=app.config['FLASKY_ADMIN'], recipients=[to])
    msg.body = render_template(template + '.txt', **kwarqs)
    msg.html = render_template(template + '.html', **kwarqs)
    thr = Thread(target=send_async_email, args=[app, msg])
    thr.start()
    return thr
    # mail.send(msg)


class NameForm(Form):
    name = StringField('what is your name?', validators=[Required()])
    submit = SubmitField('submit')


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role')

    def __repr__(self):
        return '<Role %r>' % self.name


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    def __repr__(self):
        return '<User %r>' % self.name


@app.route('/', methods=["GET", "POST"])
def index():
    # user_agent = request.headers.get('User-Agent')
    # name = None
    # env_dist = os.environ
    # for key in env_dist:
    #     print(key + ' : ' + env_dist[key])

    print(os.environ.get('MAIL_USERNAME'))

    form = NameForm()
    if form.validate_on_submit():
        # old_name = session.get('name')
        # if old_name != None and old_name != form.name.data:
        #     flash('looks like you have chenged your name')
        # session['name'] = form.name.data
        # form.name.data = ""
        user = User.query.filter_by(name=form.name.data).first()
        if user is None:
            user = User(name=form.name.data)
            db.session.add(user)
            session['known'] = False
            # if app.config['FlASY_ADMIN']:
            send_email('zhaowh3613@outlook.com', 'new user '+user.name, 'mail/new_user', user=user)
        else:
            session['known'] = True
        session['name'] = form.name.data
        form.name.data = ''
        return redirect(url_for('index'))
    return render_template('index.html', form=form, name=session.get('name'), known=session.get('known'), current_time=datetime.utcnow())


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def service_not_available(e):
    return render_template('500.html'), 500


if __name__ == '__main__':
    app.run()
