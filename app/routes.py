from app import app, lm, google_bp, db
from flask import render_template, redirect, url_for

from flask_dance.contrib.google import google
from flask_dance.consumer import oauth_authorized

from flask_login import login_required, login_user, logout_user, current_user

from app.models import User

from sqlalchemy.orm.exc import NoResultFound

import pprint

@app.route('/')
@app.route('/index')
@app.route('/goog')
def goog():
    if not google.authorized:
        return redirect(url_for('google.login'))
    resp = google.get("/plus/v1/people/me")
    assert resp.ok, resp.text
    return "You are {name} on Google".format(name=current_user.name)

@app.route('/googlogin')
def googlogin():
    return True

@oauth_authorized.connect_via(google_bp)
def google_new_login(bp, token):
    acct = bp.session.get('/plus/v1/people/me')
    if acct.ok: 
        acct_json = acct.json()
        pprint.pprint(acct_json)

        email = acct_json['emails'][0]['value']
        try:
            nickname = acct_json['nickname']
        except KeyError:
            nickname = email

        query = User.query.filter_by(email=email)

        try:
            user = query.one()
        except NoResultFound:
            user = User(name=nickname, email=email)
            db.session.add(user)
            db.session.commit()

        login_user(user)

@app.route('/logintest')
@login_required
def logintest():
    return'<h1>You are logged in as {}</h1>'.format(current_user.name)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@lm.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
