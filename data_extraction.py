from flask import Flask, jsonify
from flask_cors import CORS
import requests
import ssl
from requests.adapters import HTTPAdapter
import bcrypt
from flask import Flask, jsonify
from flask_pymongo import PyMongo
from bson import ObjectId
import logging
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})
     
app.config["MONGO_URI"] = "mongodb+srv://u19086352:Shiluvelo26*@prototype.fy7zh.mongodb.net/prototype?retryWrites=true&w=majority&appName=Prototype"

mongo = PyMongo(app)




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
    
    headers = {'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6IlNoaWx1dmVsbyIsIm5hbWUiOiJTaGlsdXZlbG8iLCJhZG1pbiI6dHJ1ZSwiaW5zdGFuY2VJZCI6IjE4Zjg0YzgxZWM5M2IyMzY3ZWFhNzQzZDhmZGJiOThjMzg1NzM2ZDUxMmUxMjY4ODc5MTgxNWVkNmMwNTk2MjMiLCJpYXQiOjE3MjcxOTk4NDYsImV4cCI6MTcyNzIyODY0Nn0.pYdCCVkrcDvMwA1mgrf_C9Ki7Ye3h1oF_BBYBuBkaSg'}
    response = session.get(url, headers=headers)

    if response.status_code == 200:
        devices = response.json()

        # Store in MongoDB with hashed IPs and prepare devices for front-end
        device_list = []
        for device in devices:
            ip_address = device['instance']['ipAddress']
            hashed_ip = bcrypt.hashpw(ip_address.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

            # Check if the device exists based on serviceName or IP address
            mongo.db.accessories.update_one(
                {'serviceName': device['serviceName']},  # Match based on serviceName (or you could use ipAddress)
                {
                    '$set': {
                        'name': device['serviceName'],
                        'hashed_ip': hashed_ip,
                        'manufacturer': device['accessoryInformation']['Manufacturer'],
                        'model': device['accessoryInformation']['Model'],
                        'firmware': device['accessoryInformation']['Firmware Revision'],
                        'ipAddress': device['instance']['ipAddress'],
                        'port': device['instance']['port']
                    }
                },
                upsert=True  # Insert a new document if it doesn't exist
            )

            # Prepare device data for front-end
            device_list.append({
                'serviceName': device['serviceName'],
                'manufacturer': device['accessoryInformation']['Manufacturer'],
                'model': device['accessoryInformation']['Model'],
                'firmware': device['accessoryInformation']['Firmware Revision'],
                'ipAddress': device['instance']['ipAddress'],
                'port': device['instance']['port']
            })
        
        return jsonify(device_list), 200
    else:
        return jsonify({'error': 'Failed to retrieve data'}), response.status_code
    

def convert_objectid_to_str(data):
    """ Recursively convert all ObjectIds to strings in a dictionary, list, or nested structure. """
    if isinstance(data, dict):
        # If data is a dictionary, recursively process key-value pairs
        return {k: convert_objectid_to_str(v) for k, v in data.items()}
    elif isinstance(data, list):
        # If data is a list, recursively process list items
        return [convert_objectid_to_str(i) for i in data]
    elif isinstance(data, ObjectId):
        # Convert ObjectId to string
        return str(data)
    else:
        # Return data unchanged if it's not a dict, list, or ObjectId
        return data

@app.route('/api/system-status', methods=['GET'])
def get_system_status():
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    ssl_context.load_cert_chain(certfile='cert.pem', keyfile='key.pem')

    session = requests.Session()
    session.mount('https://', SSLAdapter(ssl_context))

    base_url = 'http://localhost:8581/api'
    
    endpoints = {
        'cpu_status': '/status/cpu',
        'ram_status': '/status/ram',
        'network_status': '/status/network'
    }
    
    headers = {'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6IlNoaWx1dmVsbyIsIm5hbWUiOiJTaGlsdXZlbG8iLCJhZG1pbiI6dHJ1ZSwiaW5zdGFuY2VJZCI6IjE4Zjg0YzgxZWM5M2IyMzY3ZWFhNzQzZDhmZGJiOThjMzg1NzM2ZDUxMmUxMjY4ODc5MTgxNWVkNmMwNTk2MjMiLCJpYXQiOjE3MjcxOTk4NDYsImV4cCI6MTcyNzIyODY0Nn0.pYdCCVkrcDvMwA1mgrf_C9Ki7Ye3h1oF_BBYBuBkaSg'}
    
    system_data = {}
    for key, endpoint in endpoints.items():
        try:
            response = session.get(base_url + endpoint, headers=headers)
            logging.debug(f"Request to {endpoint}: {response.status_code}")
            if response.status_code == 200:
                system_data[key] = response.json()
            else:
                logging.error(f"Failed to fetch {key}. Status code: {response.status_code}, Response: {response.text}")
                system_data[key] = {'error': 'Failed to fetch'}
        except Exception as e:
            logging.error(f"Exception while fetching {key}: {e}")
            system_data[key] = {'error': str(e)}

    # Store the data in a different MongoDB collection
    # Store the data in a different MongoDB collection
    system_data_id = mongo.db.system_status.insert_one(system_data)

    # Convert ObjectId to string
    system_data['_id'] = str(system_data_id.inserted_id)

    return jsonify(convert_objectid_to_str(system_data)), 200

@app.route('/api/recent-activities', methods=['GET'])
def get_recent_activities():
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    ssl_context.load_cert_chain(certfile='cert.pem', keyfile='key.pem')

    session = requests.Session()
    session.mount('https://', SSLAdapter(ssl_context))

    url = 'http://localhost:8581/api/'  # Adjust the URL for recent activities
    headers = {'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6IlNoaWx1dmVsbyIsIm5hbWUiOiJTaGlsdXZlbG8iLCJhZG1pbiI6dHJ1ZSwiaW5zdGFuY2VJZCI6IjE4Zjg0YzgxZWM5M2IyMzY3ZWFhNzQzZDhmZGJiOThjMzg1NzM2ZDUxMmUxMjY4ODc5MTgxNWVkNmMwNTk2MjMiLCJpYXQiOjE3MjcxOTk4NDYsImV4cCI6MTcyNzIyODY0Nn0.pYdCCVkrcDvMwA1mgrf_C9Ki7Ye3h1oF_BBYBuBkaSg'}

    try:
        response = session.get(url, headers=headers)
        if response.status_code == 200:
            activities = response.json()

            # Store recent activities in MongoDB (optional)
            mongo.db.recent_activities.insert_many(activities)

            # Convert ObjectIds to strings before returning
            return jsonify(convert_objectid_to_str(activities)), 200
        else:
            return jsonify({'error': 'Failed to retrieve activities'}), response.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)