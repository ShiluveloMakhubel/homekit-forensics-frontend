from flask import Flask, jsonify
from flask_cors import CORS
import requests
import ssl
from requests.adapters import HTTPAdapter

app = Flask(__name__)
CORS(app)  # Enable CORS for all domains on all routes

class SSLAdapter(HTTPAdapter):
    def __init__(self, ssl_context=None, **kwargs):
        self.ssl_context = ssl_context
        super().__init__(**kwargs)

    def init_poolmanager(self, *args, **kwargs):
        kwargs['ssl_context'] = self.ssl_context
        return super().init_poolmanager(*args, **kwargs)

@app.route('/api/devices')
def get_devices():
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    ssl_context.load_cert_chain(certfile='cert.pem', keyfile='key.pem')

    session = requests.Session()
    session.mount('https://', SSLAdapter(ssl_context))

    url = 'http://localhost:8581/api/accessories'
    headers = {'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6IlNoaWx1dmVsbyIsIm5hbWUiOiJTaGlsdXZlbG8iLCJhZG1pbiI6dHJ1ZSwiaW5zdGFuY2VJZCI6IjE4Zjg0YzgxZWM5M2IyMzY3ZWFhNzQzZDhmZGJiOThjMzg1NzM2ZDUxMmUxMjY4ODc5MTgxNWVkNmMwNTk2MjMiLCJpYXQiOjE3MjQyMzMzNTUsImV4cCI6MTcyNDI2MjE1NX0.tloYNXnXx4TDtYOk2BKYO7ZVNDXyF5zTDvgSWC0n9iQ'}

    response = session.get(url, headers=headers)
    if response.status_code == 200:
        return jsonify(response.json()), 200
    else:
        return jsonify({'error': 'Failed to retrieve data'}), response.status_code

if __name__ == '__main__':
    app.run(debug=True)
