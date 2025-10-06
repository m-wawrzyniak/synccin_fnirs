"""
Maintaining and using LSL/REST communication to Cortiview instances.
LSL communication is used for recording start/stop, while LSL is used for marker sending.
"""
import requests
from pylsl import StreamInfo, StreamOutlet

def check_connection(device_ip, rest_port):
    """
    Checks whether PC with specific device_ip and REST port is visible.

    Args:
        device_ip (str): Device IP.
        rest_port (str): REST port of that device.

    Returns:
        bool: True if connection is healthy, False otherwise.
    """

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

def start_recording(device_ip, rest_port, save_path):
    """
    Starts Cortiview recording at specific device_ip and rest_port.
    The recording at Cortiview device will be saved in the provided save_path.

    Args:
        device_ip (str): Device IP.
        rest_port (str): REST port for the device Cortiview instance.
        save_path (str): Path at which given Cortiview instance will save the recording.

    Returns:
        bool: True if recording started. False otherwise.
    """
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
    """
    Stops Cortiview recording at specific device_ip and rest_port.

    Args:
        device_ip (str): Device IP.
        rest_port (str): REST port for the device Cortiview instance.

    Returns:
        bool: True if recording stopped. False otherwise.
    """
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
    """
    Setup ups the LSL stream, which name is specified at Cortiview configuration.

    Args:
        stream_in_name (str): Cortiview input stream name, to which markers will be sent.

    Returns:
        outlet (StreamOutlet): Outlet to which markers should be pushed.
    """
    info = StreamInfo(name=stream_in_name, type='Markers', channel_count=1,
                      channel_format='string', source_id='msi')
    outlet = StreamOutlet(info)
    return outlet

def send_marker(msg, outlet, msg_marker_map):
    """
    Sends marker with given msg, translated according to msg_marker_map to given LSL outlet.

    Args:
        msg (str): Message content.
        outlet (StreamOutlet): LSL outlet.
        msg_marker_map (dict): Translates the message into appropriate sample which will be pushed to the Cortiview Inlet.
    """
    marker = msg_marker_map[msg]
    outlet.push_sample([marker])
    print(f"Sent marker: {marker}, to {outlet}")
