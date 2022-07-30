import os
from flask import Flask, redirect, request, render_template, url_for, send_file, session
from werkzeug.utils import redirect, secure_filename

from credentials import client_id, client_secret
from credentials import authentication_url as auth_url

import requests
from requests_oauthlib import OAuth2Session

from datetime import datetime, timezone

API_ENDPOINT = "https://discord.com/api/v10"
REDIRECT_URI = "http://127.0.0.1:3000/callback"

TOKEN_URL = API_ENDPOINT + "/oauth2/token"
REVOCATION_URL = API_ENDPOINT + "/oauth2/token/revoke"
AUTHORIZATION_BASE_URL = API_ENDPOINT + "/oauth2/authorize"

app = Flask(__name__)
app.config['SECRET_KEY'] = client_secret

if 'http://' in REDIRECT_URI:
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = 'true'

def token_updater(token):
    session['oauth2_token'] = token

def make_session(token=None, state=None, scope=None):
    return OAuth2Session(
        client_id=client_id,
        token=token,
        state=state,
        scope=scope,
        redirect_uri=REDIRECT_URI,
        auto_refresh_kwargs={
            'client_id': client_id,
            'client_secret': client_secret
        },
        auto_refresh_url=TOKEN_URL,
        token_updater=token_updater
    )

def authenticate_user():
    print(session.get('oauth2_token'))
    try:
        expiry = int(str(session.get('oauth2_token')['expires_at']).split('.')[0])
        timestamp = int(str(datetime.now(timezone.utc).timestamp()).split('.')[0])
        return timestamp <= expiry
    except:
        return False


@app.route("/", methods=['POST', 'GET'])
def index():
    if authenticate_user():
        return redirect(url_for('home'))
    else:
        scope = "identify guilds guilds.members.read gdm.join".split(" ")
        discord = make_session(scope=scope)
        authorization_url, state = discord.authorization_url(AUTHORIZATION_BASE_URL)
        session['oauth2_state'] = state
        if request.method == "POST":
            print('redirecting')
            return redirect(authorization_url)
        return render_template("noauth.html")
    
@app.route("/callback", methods=['POST', 'GET'])
def callback():
    if request.values.get('error'):
        return request.values['error']
    discord = make_session(state=session.get('oauth2_state'))
    token = discord.fetch_token(
        TOKEN_URL,
        client_secret=client_secret,
        authorization_response=request.url
    )
    session['oauth2_token'] = token
    return redirect(url_for('home'))

@app.route("/home", methods=['POST', 'GET'])
def home():
    cur_token = session.get('oauth2_token')
    discord = make_session(token=cur_token)
    # do all api requests
    if request.method == "POST":
        method = request.form['submit']
        if method == "Log out":
            session.clear()
            return redirect(url_for('index'))
    try:
        user = discord.get(API_ENDPOINT + "/oauth2/@me").json()
        print(user)
        username = user['user']['username']
        avatar_url = f"https://cdn.discordapp.com/avatars/{user['user']['id']}/{user['user']['avatar']}"
        return render_template("index.html", username=username, avatar=avatar_url)
    except:
        session.clear()
        return redirect(url_for('index'))
    
@app.route("/new", methods=['POST', 'GET'])
def new():
    if authenticate_user():
        return render_template("new-event.html")
    else:
        return redirect(url_for("index"))

@app.route("/calendar", methods=['POST', 'GET'])
def calendar():
    if authenticate_user():
        date = datetime.now().strftime("%B %Y")
        return render_template("calendar.html", date=date)
    else:
        return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(port=3000, debug=True)