from flask import Flask, request,jsonify
from flask_cors import CORS
import requests
import ssl
import json
from requests.adapters import HTTPAdapter
import bcrypt
from flask_pymongo import PyMongo
from bson import ObjectId
from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash
import logging
import os
from datetime import datetime, timedelta
import hashlib

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

def add_timestamp(data):
    if isinstance(data, dict):
        data['timestamp'] = datetime.utcnow()+ timedelta(hours=2) 
    elif isinstance(data, list):
        for item in data:
            if isinstance(item, dict):
                item['timestamp'] = datetime.utcnow()+ timedelta(hours=2) 
    return data

@app.route('/api/devices')
def get_devices():
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    ssl_context.load_cert_chain(certfile='cert.pem', keyfile='key.pem')

    session = requests.Session()
    session.mount('https://', SSLAdapter(ssl_context))

    url = 'http://localhost:8581/api/accessories'
    
    headers = {'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6IlNoaWx1dmVsbyIsIm5hbWUiOiJTaGlsdXZlbG8iLCJhZG1pbiI6dHJ1ZSwiaW5zdGFuY2VJZCI6IjE4Zjg0YzgxZWM5M2IyMzY3ZWFhNzQzZDhmZGJiOThjMzg1NzM2ZDUxMmUxMjY4ODc5MTgxNWVkNmMwNTk2MjMiLCJpYXQiOjE3Mjg4OTU3NjQsImV4cCI6MTcyODkyNDU2NH0.qZNk1CGa5NbM0RUajoOhTScxQ0Zx0PViP9zT7Lf4tQA'}
    response = session.get(url, headers=headers)

    if response.status_code == 200:
        devices = response.json()

        # Store in MongoDB with hashed IPs using SHA-3
        device_list = []
        for device in devices:
            ip_address = device['instance']['ipAddress']

            # Hash the IP address using SHA-3 (256-bit)
            sha3_hasher = hashlib.sha3_256()
            sha3_hasher.update(ip_address.encode('utf-8'))
            hashed_ip = sha3_hasher.hexdigest()

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
                        'port': device['instance']['port'],
                         'timestamp': datetime.utcnow()+ timedelta(hours=2)   # Add timestamp
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
    
    headers = {'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6IlNoaWx1dmVsbyIsIm5hbWUiOiJTaGlsdXZlbG8iLCJhZG1pbiI6dHJ1ZSwiaW5zdGFuY2VJZCI6IjE4Zjg0YzgxZWM5M2IyMzY3ZWFhNzQzZDhmZGJiOThjMzg1NzM2ZDUxMmUxMjY4ODc5MTgxNWVkNmMwNTk2MjMiLCJpYXQiOjE3Mjg4OTU3NjQsImV4cCI6MTcyODkyNDU2NH0.qZNk1CGa5NbM0RUajoOhTScxQ0Zx0PViP9zT7Lf4tQA'}
    
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

    # Convert system data to JSON string and then encode to bytes
    system_data_json = json.dumps(system_data, sort_keys=True)  # Convert the data to a JSON string
    system_data_bytes = system_data_json.encode('utf-8')  # Encode the JSON string to bytes

    # Hash the system data using SHA-3 (256-bit)
    sha3_hasher = hashlib.sha3_256()
    sha3_hasher.update(system_data_bytes)
    system_data_hash = sha3_hasher.hexdigest()  # Get the hash as a hex string

    # Store the hash as part of the data
    system_data['hash'] = system_data_hash  # Store the hash as part of the stored data

    # Store the data in MongoDB
    system_data['timestamp'] = datetime.utcnow()  # Add timestamp to system status
    system_data_id = mongo.db.system_status.insert_one(system_data)
    

    # Convert ObjectId to string for JSON response
    system_data['_id'] = str(system_data_id.inserted_id)

    return jsonify(convert_objectid_to_str(system_data)), 200




@app.route('/api/recent-activities', methods=['GET'])
def get_recent_activities():
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    ssl_context.load_cert_chain(certfile='cert.pem', keyfile='key.pem')

    session = requests.Session()
    session.mount('https://', SSLAdapter(ssl_context))

    url = 'http://localhost:8581/api/server/cached-accessories'  # Adjust the URL for recent activities
    headers = {'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6IlNoaWx1dmVsbyIsIm5hbWUiOiJTaGlsdXZlbG8iLCJhZG1pbiI6dHJ1ZSwiaW5zdGFuY2VJZCI6IjE4Zjg0YzgxZWM5M2IyMzY3ZWFhNzQzZDhmZGJiOThjMzg1NzM2ZDUxMmUxMjY4ODc5MTgxNWVkNmMwNTk2MjMiLCJpYXQiOjE3Mjg4OTU3NjQsImV4cCI6MTcyODkyNDU2NH0.qZNk1CGa5NbM0RUajoOhTScxQ0Zx0PViP9zT7Lf4tQA'}

    try:
        response = session.get(url, headers=headers)
        if response.status_code == 200:
            activities = response.json()

            # Convert activities to a JSON string and encode it to bytes
            activities_json = json.dumps(activities, sort_keys=True)
            activities_bytes = activities_json.encode('utf-8')

            # Hash the activities using SHA3-256
            sha3_hasher = hashlib.sha3_256()
            sha3_hasher.update(activities_bytes)
            hashed_activities = sha3_hasher.hexdigest()  # Get the hash as a hex string

            # Insert hashed activities and original activities into MongoDB
            hashed_activities_data = add_timestamp({'hashed_activities': hashed_activities})
            mongo.db.recent_activities.insert_one(hashed_activities_data)
            mongo.db.recent_activities.insert_many(add_timestamp(activities))
            

            # Convert ObjectIds to strings before returning the response
            return jsonify(convert_objectid_to_str(activities)), 200
        else:
            return jsonify({'error': 'Failed to retrieve activities'}), response.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    



def convert_objectid_to_str(data):
    """ Recursively convert all ObjectIds to strings in a dictionary, list, or nested structure. """
    if isinstance(data, dict):
        return {k: convert_objectid_to_str(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [convert_objectid_to_str(i) for i in data]
    elif isinstance(data, ObjectId):
        return str(data)
    else:
        return data




@app.route('/api/device-logs', methods=['GET'])
def get_logs():
    try:
        with open('homebridge.log', 'r') as f:
            logs = f.readlines()
        
        # Process logs into a structure like [{"line": 1, "content": "Log entry"}]
        log_data = [{"line": index + 1, "content": log.strip()} for index, log in enumerate(logs)]

        # Convert log data to a JSON string and encode it to bytes
        log_data_json = json.dumps(log_data, sort_keys=True)
        log_data_bytes = log_data_json.encode('utf-8')

        # Hash the log data using SHA3-256
        sha3_hasher = hashlib.sha3_256()
        sha3_hasher.update(log_data_bytes)
        hashed_logdata = sha3_hasher.hexdigest()  # Get the hash as a hex string

        # Store hashed log data and original log data in MongoDB
        mongo.db.device_logs.insert_one(add_timestamp({'hashed_logdata': hashed_logdata}))
        mongo.db.device_logs.insert_many(add_timestamp(convert_objectid_to_str(log_data)))

        # **Missing return statement added here:**
        return jsonify(log_data), 200
    
    except Exception as e:
        app.logger.error(f'Error reading log file: {e}')
        return jsonify({'error': 'Could not read log file'}), 500


    


@app.route('/api/network-interfaces', methods=['GET'])
def get_network_interfaces():
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    ssl_context.load_cert_chain(certfile='cert.pem', keyfile='key.pem')

    session = requests.Session()
    session.mount('https://', SSLAdapter(ssl_context))

    url = 'http://localhost:8581/api/server/network-interfaces/system'  # Adjust the URL for network interfaces
    headers = {'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6IlNoaWx1dmVsbyIsIm5hbWUiOiJTaGlsdXZlbG8iLCJhZG1pbiI6dHJ1ZSwiaW5zdGFuY2VJZCI6IjE4Zjg0YzgxZWM5M2IyMzY3ZWFhNzQzZDhmZGJiOThjMzg1NzM2ZDUxMmUxMjY4ODc5MTgxNWVkNmMwNTk2MjMiLCJpYXQiOjE3Mjg4OTU3NjQsImV4cCI6MTcyODkyNDU2NH0.qZNk1CGa5NbM0RUajoOhTScxQ0Zx0PViP9zT7Lf4tQA'}

    try:
        response = session.get(url, headers=headers)
        if response.status_code == 200:
            activities = response.json()

            # Convert activities to a JSON string and encode it to bytes
            activities_json = json.dumps(activities, sort_keys=True)
            activities_bytes = activities_json.encode('utf-8')

            # Hash the activities using SHA3-256
            sha3_hasher = hashlib.sha3_256()
            sha3_hasher.update(activities_bytes)
            hashed_activities = sha3_hasher.hexdigest()  # Get the hash as a hex string

            # Store the hashed activities in MongoDB
            mongo.db.network_interfaces.insert_one({'hashed_activities': hashed_activities})
            mongo.db.network_interfaces.insert_many(activities)  # Insert original activities

            return jsonify(convert_objectid_to_str(activities)), 200
        else:
            return jsonify({'error': 'Failed to retrieve activities'}), response.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()  # Get the request data (JSON)
    
    username = data.get('username')
    password = data.get('password')
    
    # Find the user in the database by username
    user = mongo.db.login.find_one({'username': username})
    
    if user:
        # Check if the provided password matches the hashed password in the DB
        if check_password_hash(user['password'], password):
            # You can generate and return a token here if needed (e.g., JWT token)
            return jsonify({'message': 'Login successful', 'username': username}), 200
        else:
            return jsonify({'error': 'Invalid username or password'}), 401
    else:
        return jsonify({'error': 'Invalid username or password'}), 401
    
if __name__ == '__main__':
    app.run(debug=True)
    