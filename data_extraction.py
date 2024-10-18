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
import time

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
    
    headers = {'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6IlNoaWx1dmVsbyIsIm5hbWUiOiJTaGlsdXZlbG8iLCJhZG1pbiI6dHJ1ZSwiaW5zdGFuY2VJZCI6IjE4Zjg0YzgxZWM5M2IyMzY3ZWFhNzQzZDhmZGJiOThjMzg1NzM2ZDUxMmUxMjY4ODc5MTgxNWVkNmMwNTk2MjMiLCJpYXQiOjE3MjkyNjIxOTksImV4cCI6MTcyOTI5MDk5OX0.6zcR1_AP1YYS02e0tZspdWrfr1e4Bcl19Dx7svsBPug'}
    response = session.get(url, headers=headers)

    if response.status_code == 200:
        devices = response.json()

        # Store in MongoDB with hashed combined data using SHA-3
        device_list = []
        for device in devices:
            # Combine all relevant fields into a single string for hashing
            combined_data = (
                device['serviceName'] +
                device['accessoryInformation']['Manufacturer'] +
                device['accessoryInformation']['Model'] +
                device['accessoryInformation']['Firmware Revision'] +
                device['instance']['ipAddress'] +
                str(device['instance']['port'])
            )

            # Hash the combined string using SHA-3 (256-bit)
            sha3_hasher = hashlib.sha3_256()
            sha3_hasher.update(combined_data.encode('utf-8'))
            hashed_data = sha3_hasher.hexdigest()

            # Check if the device exists based on serviceName or hashed data
            mongo.db.accessories.update_one(
                {'serviceName': device['serviceName']},  # Match based on serviceName (or you could use hashed_data)
                {
                    '$set': {
                        'name': device['serviceName'],
                        'hashed_data': hashed_data,  # Store the hash of combined data
                        'manufacturer': device['accessoryInformation']['Manufacturer'],
                        'model': device['accessoryInformation']['Model'],
                        'firmware': device['accessoryInformation']['Firmware Revision'],
                        'ipAddress': device['instance']['ipAddress'],
                        'port': device['instance']['port'],
                        'timestamp': datetime.utcnow() + timedelta(hours=2)  # Add timestamp
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
    
    headers = {'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6IlNoaWx1dmVsbyIsIm5hbWUiOiJTaGlsdXZlbG8iLCJhZG1pbiI6dHJ1ZSwiaW5zdGFuY2VJZCI6IjE4Zjg0YzgxZWM5M2IyMzY3ZWFhNzQzZDhmZGJiOThjMzg1NzM2ZDUxMmUxMjY4ODc5MTgxNWVkNmMwNTk2MjMiLCJpYXQiOjE3MjkyNjIxOTksImV4cCI6MTcyOTI5MDk5OX0.6zcR1_AP1YYS02e0tZspdWrfr1e4Bcl19Dx7svsBPug'}
    
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
    headers = {'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6IlNoaWx1dmVsbyIsIm5hbWUiOiJTaGlsdXZlbG8iLCJhZG1pbiI6dHJ1ZSwiaW5zdGFuY2VJZCI6IjE4Zjg0YzgxZWM5M2IyMzY3ZWFhNzQzZDhmZGJiOThjMzg1NzM2ZDUxMmUxMjY4ODc5MTgxNWVkNmMwNTk2MjMiLCJpYXQiOjE3MjkyNjIxOTksImV4cCI6MTcyOTI5MDk5OX0.6zcR1_AP1YYS02e0tZspdWrfr1e4Bcl19Dx7svsBPug'}

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
        # Read the entire log file content
        with open('homebridge.log', 'r') as f:
            logs = f.readlines()  # Still using readlines() to process for API response
        
        # Process logs into a structure like [{"line": 1, "content": "Log entry"}]
        log_data = [{"line": index + 1, "content": log.strip()} for index, log in enumerate(logs)]
        
        # Convert log data to a JSON string and encode it to bytes (for hashing)
        log_data_json = json.dumps(log_data, sort_keys=True)
        log_data_bytes = log_data_json.encode('utf-8')

        # Hash the log data using SHA3-256
        sha3_hasher = hashlib.sha3_256()
        sha3_hasher.update(log_data_bytes)
        hashed_logdata = sha3_hasher.hexdigest()  # Get the hash as a hex string

        # Store the entire log file content (not individual lines) in MongoDB
        full_log_content = ''.join(logs).strip()  # Join all lines into a single string
        mongo.db.device_logs.insert_one(add_timestamp({
            'hashed_logdata': hashed_logdata,
            'log_data': full_log_content  # Store the full log content as one document
        }))

        # Return the processed log data (line by line) as JSON to the client
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
    headers = {'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6IlNoaWx1dmVsbyIsIm5hbWUiOiJTaGlsdXZlbG8iLCJhZG1pbiI6dHJ1ZSwiaW5zdGFuY2VJZCI6IjE4Zjg0YzgxZWM5M2IyMzY3ZWFhNzQzZDhmZGJiOThjMzg1NzM2ZDUxMmUxMjY4ODc5MTgxNWVkNmMwNTk2MjMiLCJpYXQiOjE3MjkyNjIxOTksImV4cCI6MTcyOTI5MDk5OX0.6zcR1_AP1YYS02e0tZspdWrfr1e4Bcl19Dx7svsBPug'}

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
    
@app.route('/api/warnings', methods=['POST'])
def store_warning():
    data = request.json
    if 'message' not in data or 'metric' not in data or 'value' not in data:
        return jsonify({'error': 'Invalid data'}), 400

    warning_message = data['message']
    metric = data['metric']
    value = data['value']
    timestamp = datetime.utcnow() + timedelta(hours=2)  # Adjust timezone as needed

    # Store the warning in MongoDB (or any other database)
    mongo.db.warnings.insert_one({
        'message': warning_message,
        'metric': metric,
        'value': value,
        'timestamp': timestamp
    })

    return jsonify({'message': 'Warning stored successfully'}), 201
'''
last_switch_status = None
last_motion_status = None  # Track the last motion status

# Database (for demonstration, using in-memory list)
switch_logs = []

# Endpoint to fetch the latest switch and motion sensor status
@app.route('/api/switch/status', methods=['GET'])
def get_switch_status():
    try:
        logs = mongo.db.switch_status.find()
        serialized_logs = [convert_objectid_to_str(log) for log in logs]  # Serialize each log entry
        return jsonify(serialized_logs), 200
    except Exception as e:
        app.logger.error(f'Error fetching logs: {e}')
        return jsonify({'error': 'Could not fetch logs'}), 500

# Helper function to log status to the database (here, an in-memory list)
def log_switch_status(switch_status, motion_status=None):
    status_str = "On" if switch_status == 1 else "Off"
    motion_str = "Detected" if motion_status == 1 else "Not Detected" if motion_status is not None else "Unknown"
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    log_entry = {
        "timestamp": timestamp,
        "status": status_str,
        "motion_status": motion_str  # Log the motion sensor status
    }

    # Print to console (for debug)
    print(f"Switch was {status_str}, Motion Sensor: {motion_str} at {timestamp}")

    log_entry_json = json.dumps(log_entry, sort_keys=True)
    log_entry_bytes = log_entry_json.encode('utf-8')

    sha3_hasher = hashlib.sha3_256()
    sha3_hasher.update(log_entry_bytes)
    hashed_logentry = sha3_hasher.hexdigest()  # Get the hash as a hex string

    # Add the hash to the log entry
    log_entry['hashed_logentry'] = hashed_logentry

    # Append log entry to switch_logs list
    switch_logs.append(log_entry)

    # Store the log entry in MongoDB
    mongo.db.switch_status.insert_one(log_entry)

# Function to fetch the switch and motion sensor status from the accessories API
def fetch_switch_status():
    global last_switch_status, last_motion_status
    try:
        response = requests.get('http://localhost:8581/api/accessories', headers={
            'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6IlNoaWx1dmVsbyIsIm5hbWUiOiJTaGlsdXZlbG8iLCJhZG1pbiI6dHJ1ZSwiaW5zdGFuY2VJZCI6IjE4Zjg0YzgxZWM5M2IyMzY3ZWFhNzQzZDhmZGJiOThjMzg1NzM2ZDUxMmUxMjY4ODc5MTgxNWVkNmMwNTk2MjMiLCJpYXQiOjE3MjkyNjIxOTksImV4cCI6MTcyOTI5MDk5OX0.6zcR1_AP1YYS02e0tZspdWrfr1e4Bcl19Dx7svsBPug',
            'accept': '*/*'
        })

        accessories = response.json()

        # Ensure the response is a list
        if isinstance(accessories, list):
            switch_status = None
            motion_status = None

            for accessory in accessories:
                if accessory.get('humanType') == "Switch":
                    switch_status = accessory.get('values', {}).get('On')

                if accessory.get('humanType') == "Motion Sensor":
                    motion_status = accessory.get('values', {}).get('MotionDetected')

                # If both switch and motion sensor statuses are found, break the loop
                if switch_status is not None and motion_status is not None:
                    break

            # Log the switch and motion sensor statuses if they changed
            if switch_status != last_switch_status or motion_status != last_motion_status:
                log_switch_status(switch_status, motion_status)
                last_switch_status = switch_status
                last_motion_status = motion_status
        else:
            print("Unexpected response format. Expected a list.")
    except Exception as e:
        print(f"Error fetching switch or motion sensor status: {e}")



# Background task to continuously check the switch status every 10 seconds
def monitor_switch():
    while True:
        fetch_switch_status()
        time.sleep(10)
import threading

# Start the monitoring in a separate thread
monitor_thread = threading.Thread(target=monitor_switch)
monitor_thread.start()
# Start monitoring the switch in the background
'''

   
if __name__ == '__main__':
    app.run(debug=True)
    