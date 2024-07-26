import requests
import json
import ssl
from requests.adapters import HTTPAdapter
from urllib3.poolmanager import PoolManager

class SSLAdapter(HTTPAdapter):
    def init_poolmanager(self, *args, **kwargs):
        context = ssl.create_default_context()
        # Disable hostname checking
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        kwargs['ssl_context'] = context
        return super(SSLAdapter, self).init_poolmanager(*args, **kwargs)

# Define the Homebridge server address and port
homebridge_url = 'https://localhost:51826'

# Define the paths to your SSL certificates
cert_path = 'cert.pem'
key_path = 'key.pem'

# Function to extract data from Homebridge
def extract_data():
    print("Starting data extraction")
    try:
        # Make a request to the Homebridge server
        print(f"Making request to {homebridge_url} with cert={cert_path} and key={key_path}")
        session = requests.Session()
        session.mount(homebridge_url, SSLAdapter())
        response = session.get(homebridge_url, cert=(cert_path, key_path), verify=False)
        print(f"Response status code: {response.status_code}")
        
        # Check if the request was successful
        if response.status_code == 200:
            # Parse the JSON response
            data = response.json()
            print("Data extracted successfully")
            print(json.dumps(data, indent=4))
        else:
            print(f"Failed to retrieve data: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Request exception occurred: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

# Run the data extraction
if __name__ == '__main__':
    extract_data()
