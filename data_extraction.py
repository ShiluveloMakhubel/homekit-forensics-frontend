import requests
import ssl
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.poolmanager import PoolManager

class SSLAdapter(HTTPAdapter):
    def __init__(self, ssl_context=None, **kwargs):
        self.ssl_context = ssl_context
        super().__init__(**kwargs)

    def init_poolmanager(self, *args, **kwargs):
        kwargs['ssl_context'] = self.ssl_context
        return super().init_poolmanager(*args, **kwargs)

# Create an SSL context
ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
ssl_context.load_cert_chain(certfile='cert.pem', keyfile='key.pem')

session = requests.Session()
session.mount('https://', SSLAdapter(ssl_context))

# Define the URL and headers
url = 'http://localhost:8581/api/status/ram'  # Target the specific API endpoint
headers = {
    'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6IlNoaWx1dmVsbyIsIm5hbWUiOiJTaGlsdXZlbG8iLCJhZG1pbiI6dHJ1ZSwiaW5zdGFuY2VJZCI6IjE4Zjg0YzgxZWM5M2IyMzY3ZWFhNzQzZDhmZGJiOThjMzg1NzM2ZDUxMmUxMjY4ODc5MTgxNWVkNmMwNTk2MjMiLCJpYXQiOjE3MjMwNTY0ODgsImV4cCI6MTcyMzA4NTI4OH0.lCMs96Y7krfjyPTpddYxLu8DwKRvHAbaCtSqs1dLJKw',}

try:
    response = session.get(url, headers=headers, verify=False)  # 'verify=False' to skip SSL verification
    print(f"Response status code: {response.status_code}")
    if response.status_code == 200:
        print("Data retrieved successfully:")
        try:
            json_data = response.json()
            print(json_data)
        except ValueError:
            print("Response content is not valid JSON")
    else:
        print(f"Failed to retrieve data: {response.status_code}")
except requests.exceptions.RequestException as e:
    print(f"Request exception occurred: {e}")
