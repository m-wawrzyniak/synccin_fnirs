from psychopy import sound, gui, visual, core, data, event, logging, clock, colors, layout, monitors
import psychopy.iohub as io
from psychopy.hardware import keyboard
import ast

import m01_procedure_setup as setup
import m02_psychopy_routines as routines
from config import WIN_ID_MAIN, WIN_ID_MASTER, WIN_SIZES
from config import CALIB_ANI_1_PATH, CALIB_ANI_2_PATH, CALIB_ANI_3_PATH
from config import PHOTO_POS
from config import MOVIE_1_PATH, MOVIE_2_PATH, MOVIE_3_PATH


### STAGE 1: SETUP

# PsychoPy setup
expInfo, thisExp, logFile, log_path = setup.setup_path_log_psychopy()

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

# TODO: There would be zmq setup between PCs


### STAGE 2: CALIBRATION
# TODO: There is no calibration, so this stage is useless
if start_stage <= 2 and True==False:

    # 1. VERBATIM: Initialize calibration animations
    calib_anim_1 = visual.MovieStim(win_main, CALIB_ANI_1_PATH, size=WIN_SIZES[WIN_ID_MAIN])
    print('calib_anim_1 initialized...')

    # 2. INTERRUPT:
    routines.interrupt('Press \'x\' to begin calibration instruction...', win_master)

    # 3. ROUTINE:
    routines.setup_routine_components([calib_anim_1])
    # TODO: Would send annotation start_calib_anim_1
    routines.run_routine(win=win_main,
                         routine_components = [calib_anim_1],
                         routine_timer=routineTimer,
                         defaultKeyboard=defaultKeyboard,
                         duration=calib_anim_1.duration if not debug_mode else 5)
    # TODO: Would send annotation stop_calib_anim_1


### STAGE 3: MOVIES
movies = None

if start_stage <= 3:
    # TODO: Start fNIRS recording

    # 1. VERBATIM: Initializing stimuli
    movies, rand_movies, photo_rect_on, photo_rect_off, cross = setup.setup_main_stimuli(win_main,
                                                                                         MOVIE_1_PATH, MOVIE_2_PATH, MOVIE_3_PATH,
                                                                                         photo_pos=PHOTO_POS)
    expInfo['mov_order'] = rand_movies  # Save the order of the movies
    cross.draw()  # Draw focus cross before the first movie
    win_main.flip()  # Refresh window
    # TODO: Pytanie, czy informowac fNIRS o kazdej zmianie w procedurze ktora wplywa na to co widzi badany.

    # 2. INTERRUPT: Start main procedure
    routines.interrupt('Press \'x\' to begin stimulus procedure...', win_master)

    # 3. ROUTINE: Present movies
    for i in range(len(rand_movies)):
        # Movie setup
        mov_name = rand_movies[i] # Pick movie
        movie = movies[mov_name] # Pack it into components list
        routines.setup_routine_components([movie]) # Set it up for routine

        # TODO: Send that movie started marker

        # Running routine
        #movie.reset()  # Synchronize audio with video.
        routines.run_stimulus_routine(win_main,
                                      mov_name, movie, photo_rect_on, photo_rect_off,
                                      routineTimer, thisExp, defaultKeyboard,
                                      movie_duration=movie.duration if not debug_mode else 10)

        # TODO: Send that movie finished

        # Setup and present fixation cross between the movies and at the end of movie sequence presentation
        routines.setup_routine_components([cross])
        routines.run_routine(win=win_main,
                             routine_components = [cross],
                             routine_timer=routineTimer,
                             defaultKeyboard=defaultKeyboard,
                             duration=10)

    # 4. VERBATIM: Ending recording
    # TODO: Stop fNIRS recording


### STAGE 4: FREE CONVERSATIOM
if start_stage <= 4:
    if movies is None:
        photo_rect_on, photo_rect_off = setup.setup_free_convo_stimuli(win_main)

    # Fetching info about the free conversation
    free_convos = ['first', 'second']
    convo_countdown = int(expInfo['free conversation countdown'])
    convo_len = int(expInfo['free conversation length'])

    for i in free_convos:
        routines.interrupt(f'Press \'x\' to begin {i} free conversation...', win_master)

        # TODO: fNIRS starting recording

        routines.run_free_convo_routine(win=win_main, win_master=win_master,
                                        photo_rect_on=photo_rect_on, photo_rect_off=photo_rect_off,
                                        convo_countdown=convo_countdown, convo_len=convo_len,
                                        routineTimer=routineTimer)

        # TODO: Stopping conversation


### STAGE 5: WRAPPING UP
thisExp.saveAsPickle(log_path)
logging.flush()
thisExp.abort()  # This will cancel ExperimentHandler save during core.quit()
win_main.close()
win_master.close()
core.quit()