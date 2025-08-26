import requests
import json
from pylsl import resolve_byprop, StreamInlet
from pylsl import StreamInfo, StreamOutlet

def check_connection(device_ip, rest_port):
    url = f"http://{device_ip}:{rest_port}/health"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            print(f"Device at {device_ip}:{rest_port} is healthy.")
            return True
        else:
            print(f"Health check failed: {response.status_code} {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"Could not connect to {device_ip}:{rest_port} — {e}")
        return False

def start_calibration(rest_port, template_path):
    # TODO: calibration handler wymaga konkretnego formatu *json do rozpoczęcia kalibracji, jednak nie wiem jeszcze jakiego.
    url = f"http://localhost:{rest_port}/calibrateNirs"
    try:
        with open(template_path, 'r') as f:
            data = json.load(f)

        response = requests.post(url, json=data)
        if response.status_code == 200:
            print(f"Calibration started at {rest_port}")
            return True
        else:
            print(f"Failed to start calibration: {response.status_code} {response.text}")
            return False

    except requests.exceptions.RequestException as e:
        print(f"Error connecting to CortiView: {e}")
        return False

def start_recording(device_ip, rest_port, save_path):
    url = f"http://{device_ip}:{rest_port}/startRecord?filename={save_path}"
    try:
        response = requests.post(url)
        if response.status_code == 200:
            print(f"Recording started at {rest_port}:{save_path}")
            return True
        else:
            print(f"Failed to start recording at {device_ip}:{rest_port}: {response.status_code} {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to CortiView: {e}")
        return False

def stop_recording(device_ip, rest_port):
    url = f"http://{device_ip}:{rest_port}/stopRecord"
    try:
        response = requests.post(url)
        if response.status_code == 200:
            print(f"Recording stopped at {device_ip}:{rest_port}")
            return True
        else:
            print(f"Failed to stop recording at {device_ip}:{rest_port}: {response.status_code} {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to CortiView: {e}")
        return False

def setup_lsl_channel(stream_in_name):
    info = StreamInfo(name=stream_in_name, type='Markers', channel_count=1,
                      channel_format='string', source_id='msi')
    outlet = StreamOutlet(info)
    return outlet

def send_marker(msg, outlet, msg_marker_map):
    marker = msg_marker_map[msg]
    outlet.push_sample([marker])
    print(f"Sent marker: {marker}, to {outlet}")
    #time.sleep(1)
