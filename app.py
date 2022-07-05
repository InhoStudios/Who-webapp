import os
from flask import Flask, redirect, request, render_template, url_for, send_file, session
from werkzeug.utils import redirect, secure_filename

from credentials import client_id, client_secret
from credentials import authentication_url as auth_url

from discord_manager import DiscordManager

import requests
from requests_oauthlib import OAuth2Session

API_ENDPOINT = "https://discord.com/api/v10"
REDIRECT_URI = "http://127.0.0.1:3000/callback"

TOKEN_URL = API_ENDPOINT + "/oauth2/token"
AUTHORIZATION_BASE_URL = API_ENDPOINT + "/oauth2/authorize"

app = Flask(__name__)
app.config['SECRET_KEY'] = client_secret

if 'http://' in REDIRECT_URI:
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = 'true'

dm = DiscordManager()

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

@app.route("/", methods=['POST', 'GET'])
def index():
    scope = "identify guilds.members.read gdm.join".split(" ")
    discord = make_session(scope=scope)
    authorization_url, state = discord.authorization_url(AUTHORIZATION_BASE_URL)
    session['oauth2_state'] = state
    try:
        code = request.args['code']
        print(code)
    except:
        return render_template("noauth.html", auth_url=authorization_url)
    
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
    return redirect(url_for('.home'))

@app.route("/home", methods=['POST', 'GET'])
def home():
    discord = make_session(token=session.get('oauth2_token'))
    user = discord.get(API_ENDPOINT + "/users/@me").json()
    print(user)
    username = user['username']
    return render_template("index.html", username=username)

if __name__ == "__main__":
    app.run(port=3000, debug=True)