# global
PROCEDURE_SAVE_DIR = "C:/Users/Badania/OneDrive/Pulpit/Syncc-In/fnirs_data"
WIFI_NAME = 'cortivision_mobile'
WIFI_PASS = 'fnirs2024'

REST_API_PORT_CHILD = '8888'
REST_API_PORT_CAREGIVER = '8888'

CHILD_IP = "localhost"
CAREGIVER_IP = "192.168.76.100"

MARKER_MAP = {
    'm1_start': '1',
    'm1_stop': '2',
    'm2_start': '3',
    'm2_stop': '4',
    'm3_start': '5',
    'm3_stop': '6',
    'fc1_start': '7',
    'fc1_stop': '8',
    'fc2_start': '9',
    'fc2_stop': '10'
}

FRAME_TOLERANCE = 0.005

# m01_procedure_setup.py
LOG_DIR = f"{PROCEDURE_SAVE_DIR}/psychopy_logs"

WIN_ID_MASTER = 1
WIN_ID_MAIN = 0
WIN_SIZES = [None, None]
WIN_SIZES[WIN_ID_MASTER] = (1920,1080)
WIN_SIZES[WIN_ID_MAIN] = (2560, 1440)

MOVIES_DIR = "C:/movies_et"

MOVIE_1_PATH = f'{MOVIES_DIR}/norm_mov1.mp4'
MOVIE_2_PATH = f'{MOVIES_DIR}/norm_mov2.mp4'
MOVIE_3_PATH = f'{MOVIES_DIR}/norm_mov3.mp4'

PHOTO_POS = (1, 0)


FNIRS_MONTAGE_PATH = "C:/syncc_in/Cortiview 2/SYNCCIN_31_07.montage"
FNIRS_TEMPLATE_PATH = "C:/syncc_in/Cortiview 2/SYNCCIN_31_07.montage_template.template"


LSL_CHILD_INPUT = 'cv_child_marker_in'
LSL_CHILD_OUTPUT = 'cv_child_marker_out'
LSL_CHILD_DATA_OUTPUT = 'cv_child_data_out'

LSL_CAREGIVER_INPUT = 'cv_caregiver_marker_in'
LSL_CAREGIVER_OUTPUT = 'cv_caregiver_marker_out'
LSL_CAREGIVER_DATA_OUTPUT = 'cv_caregiver_data_out'