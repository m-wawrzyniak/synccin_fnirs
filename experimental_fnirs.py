from pylsl import resolve_byprop, StreamInlet
from pylsl import StreamInfo, StreamOutlet
import time
import requests

from config import LSL_CHILD_INPUT, LSL_CHILD_OUTPUT, LSL_CHILD_DATA_OUTPUT
from config import LSL_CAREGIVER_INPUT, LSL_CAREGIVER_OUTPUT, LSL_CAREGIVER_DATA_OUTPUT


def get_markers(stream_name):
    """
    Sees the markers when pressed on CortiView. OK
    :return:
    """
    # Find the output marker stream from CortiView
    streams = resolve_byprop('name', 'cortivision_markers_out', timeout=5)
    if not streams:
        raise RuntimeError("Stream not found!")
    inlet = StreamInlet(streams[0])

    # Read markers
    while True:
        sample, timestamp = inlet.pull_sample()
        print(f"Received marker: {sample[0]} at {timestamp}")

def send_marker():
    """
    To send markers reliably, you need to start LSL waay before the registration with Cortiview.
    So here there is 50 seconds before sending markers.
    Sending them as '1' and '2' (str) IS VISIBLE IN CortiView GUI.
    Even numbers over 8 are visible on GUI
    Sending any other strings - NOT VISIBLE in GUI - but maybe visible in registration.
    :return:
    """
    """
    In original demo:
    IN PSYEXP:
    <Param name="conditions" updates="None" val="[OrderedDict([('trialText', 'LEFT'), ('trigger', 1)]), OrderedDict([('trialText', 'RIGHT'), ('trigger', 2)])]" valType="str"/>
    
    IN PY:
    info = StreamInfo(name='cortivision_markers_out', type='Markers', channel_count=1,
                      channel_format='int32', source_id='uniqueid12345')
    outlet = StreamOutlet(info)
    
        text.setText('TAP FINGERS OF YOUR ' + trialText + ' HAND')
    outlet.push_sample(x=[trigger])
    
    
    
    """

    info = StreamInfo(name='cortivision_markers', type='Markers', channel_count=1,
                      channel_format='string', source_id='eloelo')
    outlet = StreamOutlet(info)

    print("Stream created. Waiting for CortiView to subscribe...")
    time.sleep(50)

    markers = ['1', '2', '10', 'STOP']
    for marker in markers:
        outlet.push_sample([marker])
        print(f"Sent marker: {marker}")
        time.sleep(1)  # Wait to ensure CortiView receives it

def get_data():
    """
    Gets the data ad hoc!!!
    Dont know the format yet, but looks promising.
    :return:
    """

    # Resolve the data stream
    streams = resolve_byprop('name', 'cortivision_data', timeout=5)
    if not streams:
        raise RuntimeError("Stream not found!")
    inlet = StreamInlet(streams[0])

    # Pull samples continuously
    while True:
        sample, timestamp = inlet.pull_sample()
        print(f"Data: {sample} at {timestamp}")

def start_cortiview_recording(filename: str = "session"):
    """
    Sends a REST command to CortiView2 to start recording.

    :param filename: The filename to save the recording as (no extension needed).
    :return: True if successful, False otherwise.
    """
    url = f"http://localhost:8888/startRecord?filename={filename}"
    try:
        response = requests.post(url)
        if response.status_code == 200:
            print(f"✅ Recording started: {filename}")
            return True
        else:
            print(f"❌ Failed to start recording: {response.status_code} {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"⚠️ Error connecting to CortiView: {e}")
        return False

# finding caregiver
streams = resolve_byprop('name', LSL_CAREGIVER_OUTPUT, timeout=5)
if not streams:
    raise RuntimeError("Stream not found!")
caregiver_inlet = StreamInlet(streams[0])

# finding child
streams = resolve_byprop('name', LSL_CHILD_OUTPUT, timeout=5)
if not streams:
    raise RuntimeError("Stream not found!")
child_inlet = StreamInlet(streams[0])

# Read markers
while True:
    ch_sample, ch_timestamp = child_inlet.pull_sample()
    cg_sample, cg_timestamp = caregiver_inlet.pull_sample()
    print(f"Received markers: \n child {ch_sample[0]} at {ch_timestamp} \n caregiver {cg_sample[0]} at {cg_timestamp}")