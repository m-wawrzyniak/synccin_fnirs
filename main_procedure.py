"""
PROCEDURE SETUP:
1. Devices within the procedure:
    - MSI PC (001)
    - Dell PC (002)
    - Two CortiVision fNIRS devices.
2. All devices are connected to a single WI-FI - WIFI_NAME.
3. Both PCs have to open the CortiView instances by themselves.
4. On both PCs, proper channel templates have to be manually chosen.
5. At this point it's assumed that the diade has the caps on.
6. Then, run the procedure.

PROCEDURE TIMELINE:
0. Diade metadata input.
1. Calibration is started in both CortiView instaces.
2. Start plotting on both CortiView instances.
3. Start recording on both CortiView instances.
3. Show three videos. Proper marking.
4. Stop recording on both CortiView instances.
"""
import time

from psychopy import sound, gui, visual, core, data, event, logging, clock, colors, layout, monitors
import numpy as np

import m01_procedure_setup as setup
import m02_psychopy_routines as routines
import m03_cortiview_comms as comms


from config import WIN_ID_MAIN, WIN_ID_MASTER, WIN_SIZES
from config import PHOTO_POS
from config import CHILD_IP, REST_API_PORT_CHILD, CAREGIVER_IP, REST_API_PORT_CAREGIVER
from config import LSL_CHILD_INPUT, LSL_CAREGIVER_INPUT
from config import MARKER_MAP
from config import MOVIE_1_PATH, MOVIE_2_PATH, MOVIE_3_PATH

### STAGE 1: SETUP

# PsychoPy setup
expInfo, thisExp, logFile, log_path = setup.setup_path_log_psychopy()

expInfo['marker_map'] = str(MARKER_MAP)
if expInfo['debug mode'] == 'True':  # whether it should run in debug mode
    debug_mode = True
else:
    debug_mode = False
start_stage = int(expInfo['start at stage'][0])  # skip to specific stage

globalClock = core.Clock()  # to track the time since experiment started
routineTimer = core.Clock()  # to track time remaining of each (possibly non-slip) routine
endExpNow = False  # flag for 'escape' or other condition => quit the exp

# Screen setup
#setup.check_screen_id_assignment()
win_main, win_master, gigabyte_mon, test_mon = setup.setup_windows(win_id_master=WIN_ID_MASTER, win_id_main=WIN_ID_MAIN, expInfo=expInfo)
defaultKeyboard = setup.io_setup(win_main, expInfo=expInfo)

# Paths setup
cortiview_filename = setup.create_cortiview_recording_name(expInfo)

# TODO: Verify whether there really are only 4 devices in the network - maybe even with specific IP.
# Check if CortiVisions are setup:
comms.check_connection(device_ip=CHILD_IP, rest_port=REST_API_PORT_CHILD)
comms.check_connection(device_ip=CAREGIVER_IP, rest_port=REST_API_PORT_CAREGIVER)
# Create LSL Outlets:
child_outlet = comms.setup_lsl_channel(stream_in_name=LSL_CHILD_INPUT)
caregiver_outlet = comms.setup_lsl_channel(stream_in_name=LSL_CAREGIVER_INPUT)

### STAGE 2: CALIBRATION
if start_stage <= 2:
    routines.interrupt('Press \'x\', when fNIRS caps are properly set. This will start automatic calibration of caregiver fNIRS', win_master, ['x'])
    #comms.start_calibration(rest_port=REST_API_PORT_CAREGIVER, template_path="C:/syncc_in/Cortiview 2/test_child.template")
    routines.interrupt('Press \'x\', when caregiver calibration has been successful. This will start automatic calibration of child fNIRS', win_master, ['x'])
    #comms.start_calibration(rest_port=REST_API_PORT_CHILD, template_path="C:/syncc_in/Cortiview 2/test_child.template")

### STAGE 3: MOVIES
routines.interrupt('Press \'x\', when calibration has been successful. This will start recording and initialize the stimuli.', win_master, ['x'])
movie_paths = None

if start_stage <= 3:

    # 0. Starting fNIRS recording
    comms.start_recording(device_ip= CHILD_IP, rest_port=REST_API_PORT_CHILD,
                          save_path=f'{cortiview_filename}_d_movies')
    comms.start_recording(device_ip= CAREGIVER_IP, rest_port=REST_API_PORT_CAREGIVER,
                          save_path=f'{cortiview_filename}_m_movies')

    # 1. VERBATIM: Initializing stimuli
    photo_rect_on, photo_rect_off, cross = setup.setup_helper_stimuli(win_main, photo_pos=PHOTO_POS)

    movie_paths = {'m1': MOVIE_1_PATH, 'm2': MOVIE_2_PATH, 'm3': MOVIE_3_PATH}
    rand_movies = list(np.random.permutation(list(movie_paths.keys())))

    expInfo['mov_order'] = rand_movies  # Save the order of the movies
    cross.draw()  # Draw focus cross before the first movie
    win_main.flip()  # Refresh window

    # 2. INTERRUPT: Start main procedure
    routines.interrupt('Press \'x\' to begin stimulus procedure...', win_master)

    # 3. ROUTINE: Present movies
    for i in range(len(rand_movies)):
        # Movie setup
        mov_name = rand_movies[i] # Pick movie
        movie_path = movie_paths[mov_name] # Pack it into components list
        print(f'Initializing {mov_name}...')
        movie = visual.MovieStim(win_main, movie_path, size=(2560, 1440))
        print(f'{mov_name} initialized.')

        routines.setup_routine_components([movie]) # Set it up for routine

        # Sending markers for movie start
        comms.send_marker(msg=f"{mov_name}_start", outlet=child_outlet, msg_marker_map=MARKER_MAP)
        comms.send_marker(msg=f"{mov_name}_start", outlet=caregiver_outlet, msg_marker_map=MARKER_MAP)

        # Running routine
        #movie.reset()  # Synchronize audio with video.
        routines.run_stimulus_routine(win_main,
                                      mov_name, movie, photo_rect_on, photo_rect_off,
                                      routineTimer, thisExp, defaultKeyboard,
                                      movie_duration=movie.duration if not debug_mode else 10)

        # Sending markers for movie stop
        comms.send_marker(msg=f"{mov_name}_stop", outlet=child_outlet, msg_marker_map=MARKER_MAP)
        comms.send_marker(msg=f"{mov_name}_stop", outlet=caregiver_outlet, msg_marker_map=MARKER_MAP)

        # Setup and present fixation cross between the movies and at the end of movie sequence presentation
        routines.setup_routine_components([cross])
        routines.run_routine(win=win_main,
                             routine_components = [cross],
                             routine_timer=routineTimer,
                             defaultKeyboard=defaultKeyboard,
                             duration=10)

    # 4. VERBATIM: Ending recording
    comms.stop_recording(device_ip=CHILD_IP, rest_port=REST_API_PORT_CHILD)
    comms.stop_recording(device_ip=CAREGIVER_IP, rest_port=REST_API_PORT_CAREGIVER)


### STAGE 4: FREE CONVERSATIOM
if start_stage <= 4:
    if movie_paths is None:
        photo_rect_on, photo_rect_off = setup.setup_free_convo_stimuli(win_main)

    # Fetching info about the free conversation
    free_convos = ['fc1', 'fc2']
    convo_countdown = int(expInfo['free conversation countdown'])
    convo_len = int(expInfo['free conversation length'])

    for i in free_convos:
        routines.interrupt(f'Press \'x\' to begin {i}...', win_master)

        # Starting recording
        comms.start_recording(device_ip=CHILD_IP, rest_port=REST_API_PORT_CHILD,
                              save_path=f'{cortiview_filename}_d_{i}')
        comms.start_recording(device_ip=CAREGIVER_IP, rest_port=REST_API_PORT_CAREGIVER,
                              save_path=f'{cortiview_filename}_d_{i}')

        time.sleep(1)
        comms.send_marker(msg=f'{i}_start', outlet=child_outlet, msg_marker_map=MARKER_MAP)
        comms.send_marker(msg=f'{i}_start', outlet=caregiver_outlet, msg_marker_map=MARKER_MAP)

        # Free convo
        routines.run_free_convo_routine(win=win_main, win_master=win_master,
                                        photo_rect_on=photo_rect_on, photo_rect_off=photo_rect_off,
                                        convo_countdown=convo_countdown, convo_len=convo_len,
                                        routineTimer=routineTimer)

        # Stopping recording
        comms.send_marker(msg=f'{i}_stop', outlet=child_outlet, msg_marker_map=MARKER_MAP)
        comms.send_marker(msg=f'{i}_stop', outlet=caregiver_outlet, msg_marker_map=MARKER_MAP)

        comms.stop_recording(device_ip=CHILD_IP, rest_port=REST_API_PORT_CHILD)
        comms.stop_recording(device_ip=CAREGIVER_IP, rest_port=REST_API_PORT_CAREGIVER)


### STAGE 5: WRAPPING UP
thisExp.saveAsPickle(log_path)
logging.flush()
thisExp.abort()  # This will cancel ExperimentHandler save during core.quit()
win_main.close()
win_master.close()
core.quit()