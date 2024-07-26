# auth.py
from flask import Flask, redirect, url_for, session
from authlib.integrations.flask_client import OAuth

app = Flask(__name__)
app.secret_key = 'random_secret_key'
oauth = OAuth(app)

app.config['OAUTH_CREDENTIALS'] = {
    'client_id': 'your_client_id',
    'client_secret': 'your_client_secret',
    'redirect_uri': 'http://localhost:5000/callback'
}

oauth.register(
    name='example',
    client_id=app.config['OAUTH_CREDENTIALS']['client_id'],
    client_secret=app.config['OAUTH_CREDENTIALS']['client_secret'],
    authorize_url='https://example.com/oauth/authorize',
    access_token_url='https://example.com/oauth/token',
    client_kwargs={'scope': 'openid profile email'}
)

@app.route('/login')
def login():
    redirect_uri = url_for('authorize', _external=True)
    return oauth.example.authorize_redirect(redirect_uri)

@app.route('/callback')
def authorize():
    token = oauth.example.authorize_access_token()
    user = oauth.example.parse_id_token(token)
    return jsonify(user)
