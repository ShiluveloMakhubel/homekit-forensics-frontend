# app.py (updated)
from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "HomeKit Forensics API"

if __name__ == '__main__':
    app.run(ssl_context=('cert.pem', 'key.pem'), debug=True)
