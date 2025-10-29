import pickle
from pprint import pprint
import time
"""
name = "C://Users//Badania//OneDrive//Pulpit//Syncc-In//fnirs_data//psychopy_logs//W_058_et_syncc_in_procedure_2025-09-20_12h24.55.946.psydat"
try:
    with open(name, 'rb') as f:
        dane = pickle.load(f)
    # Tutaj możesz pracować z odzyskanymi danymi
    print("expInfo (extraInfo):")
    pprint(dane.extraInfo)
except FileNotFoundError:
    print("Plik nie został znaleziony.")
except Exception as e:
    print(f"Wystąpił błąd podczas odczytu pliku: {e}")
"""
import os
os.environ["LSL_NO_IPV6"] = "1"
from config import CAREGIVER_IP, REST_API_PORT_CAREGIVER, LSL_CAREGIVER_INPUT, MARKER_MAP
from config import CHILD_IP, REST_API_PORT_CHILD, LSL_CHILD_INPUT
import m03_cortiview_comms as comms


comms.check_connection(device_ip=CAREGIVER_IP, rest_port=REST_API_PORT_CAREGIVER)
caregiver_outlet = comms.setup_lsl_channel(stream_in_name=LSL_CAREGIVER_INPUT)
time.sleep(6)
comms.start_recording(device_ip=CAREGIVER_IP, rest_port=REST_API_PORT_CAREGIVER,
                      save_path=f'test_m_movies')
comms.send_marker(msg=f"m1_start", outlet=caregiver_outlet, msg_marker_map=MARKER_MAP)

"""
comms.check_connection(device_ip=CHILD_IP, rest_port=REST_API_PORT_CHILD)
child_outlet = comms.setup_lsl_channel(stream_in_name=LSL_CHILD_INPUT)
time.sleep(1)
comms.send_marker(msg=f"m1_start", outlet=child_outlet, msg_marker_map=MARKER_MAP)
"""