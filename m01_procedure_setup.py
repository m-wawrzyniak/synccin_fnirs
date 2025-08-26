import os
import zmq
import time
import numpy as np
import ast
import pyglet

from numpy.random import random, randint, normal, shuffle, choice as randchoice
from psychopy import sound, gui, visual, core, data, event, logging, clock, colors, layout, monitors
import msgpack
import psychopy.iohub as io
from psychopy.hardware import keyboard


from config import LOG_DIR, WIN_SIZES

def setup_path_log_psychopy():
    """
    Setup paths and logs for ET procedure.

    Returns:
        - expInfo (dict) Dictionary of experiment information (name:value)
        - thisExp (ExperimentHandler) ???
        - logFile (LogFile) ???
        - filename (str) Absolute path for saving all data and logs.
    """
    os.makedirs(LOG_DIR, exist_ok=True)
    os.chdir(LOG_DIR)

    # Info about experimental session and what goes into GUI dialog
    psychopyVersion = '2024.2.4'
    expName = 'et_syncc_in_procedure'
    expInfo = {
        'participant': f"{randint(0, 999999):06.0f}",
        'session': '001',
        'window background color': '[0.0, 0.0, 0.0]',
        'free conversation countdown': '30',
        'free conversation length': '180',
        'debug mode': ['False', 'True'],
        'start at stage': ['2. Calibration', '3. Movies', '4. Free convo']
    }
    print(f"Syncc-In ET procedure, participant: {expInfo['participant']}")

    # Participant info dialog
    session_win = True
    if session_win:
        dlg = gui.DlgFromDict(dictionary=expInfo, sortKeys=False, title=expName)
        if not dlg.OK:
            core.quit()  # user pressed cancel
    expInfo['date'] = data.getDateStr()
    expInfo['expName'] = expName
    expInfo['psychopyVersion'] = psychopyVersion

    # Data file name stem = absolute path + name; later add .psyexp, .csv, .log, etc
    log_path = f"{LOG_DIR}/{str(expInfo['participant'])}_{expName}_{expInfo['date']}"

    # An ExperimentHandler isn't essential but helps with data saving
    thisExp = data.ExperimentHandler(name=expName, version='',
                                     extraInfo=expInfo, runtimeInfo=None,
                                     originPath=LOG_DIR,
                                     savePickle=True, saveWideText=True,
                                     dataFileName="experimental_handler")

    # save a log file for detail verbose info
    logFile = logging.LogFile(log_path + '.log', level=logging.EXP)
    logging.console.setLevel(logging.WARNING)  # this outputs to the screen, not a file



    return expInfo, thisExp, logFile, log_path

def io_setup(main_win, expInfo):
    ioConfig = {}
    ioConfig['Keyboard'] = dict(use_keymap='psychopy')
    ioServer = io.launchHubServer(window=main_win, **ioConfig)
    defaultKeyboard = keyboard.Keyboard(backend='iohub')
    ioSession = '1'
    if 'session' in expInfo:
        ioSession = str(expInfo['session'])

    return defaultKeyboard

def check_screen_id_assignment():
    screens = pyglet.canvas.get_display().get_screens()

    for i, screen in enumerate(screens):
        print(f"Screen {i}: {screen.width}x{screen.height}, x={screen.x}, y={screen.y}")
        if screen.width != WIN_SIZES[i][0] or screen.height != WIN_SIZES[i][1]:
            raise TypeError('Screen IDs are wrong!')

def setup_windows(win_id_master, win_id_main, expInfo):
    all_monitors = monitors.getAllMonitors()
    print(f"Available monitors: {all_monitors}")

    # Define monitor specifications
    gigabyte_monitor = monitors.Monitor('GIGABYTE')
    gigabyte_monitor.setWidth(52.7)  # Width in cm (adjust for your monitor)
    gigabyte_monitor.setSizePix([2560, 1440])  # Resolution
    gigabyte_monitor.setDistance(57)  # Distance from the screen in cm
    gigabyte_monitor.saveMon()  # Save the monitor configuration

    test_monitor = monitors.Monitor('testMonitor')
    test_monitor.setWidth(30.0)  # Width in cm (adjust for your monitor)
    test_monitor.setSizePix([640, 480])  # Resolution
    test_monitor.setDistance(50)  # Distance from the screen in cm
    test_monitor.saveMon()  # Save the monitor configuration

    bckgnd_clr_str = expInfo['window background color']  # Get bckgnd color from UI
    try:
        background_clr = ast.literal_eval(bckgnd_clr_str)  # Convert it to a list of RGB
    except:
        background_clr = None

    if background_clr is None:
        background_clr = [-1.0, -1.0, -1.0]

    win_main = visual.Window(
        size=[2560, 1440], fullscr=False, screen=win_id_main,
        winType='pyglet', allowStencil=False,
        monitor=gigabyte_monitor, color=background_clr, colorSpace='rgb',
        blendMode='avg', useFBO=True,
        units='norm', checkTiming=False)
    win_main.mouseVisible = True

    win_master = visual.Window(
        size=[640, 480], fullscr=False, screen=win_id_master,
        winType='pyglet', allowStencil=False,
        monitor=test_monitor, color=background_clr, colorSpace='rgb',
        blendMode='avg', useFBO=True,
        units='norm', checkTiming=False)
    print("Windows defined")

    return win_main, win_master, gigabyte_monitor, test_monitor

def create_cortiview_recording_name(expInfo):
    ses_date, ses_time = expInfo['date'][:-7].split('_')
    ses_date = ses_date.replace('-', '_')
    ses_time = ses_time.replace('h', '')
    cortiview_filename = f"{ses_date}_fnirs_{ses_time}_{expInfo['participant']}"

    return cortiview_filename


def setup_helper_stimuli(win, photo_pos):

    # Photodiode rectangle init
    size = 0.1
    photo_rect_on = visual.Rect(
        win=win, name='photo_rect_on',
        width=size * (9 / 16), height=size, units='norm',
        ori=0.0, pos=photo_pos, anchor='bottom-right',
        lineWidth=1.0, colorSpace='rgb', lineColor='white', fillColor='white',
        opacity=None, depth=0.0, interpolate=True)

    size = 0.1
    photo_rect_off = visual.Rect(
        win=win, name='photo_rect_off',
        width=size * (9 / 16), height=size, units='norm',
        ori=0.0, pos=photo_pos, anchor='bottom-right',
        lineWidth=1.0, colorSpace='rgb', lineColor='black', fillColor='black',
        opacity=None, depth=0.0, interpolate=True)

    # Cross stimuli init
    cross = visual.ShapeStim(
        win=win,
        vertices='cross',  # Define shape as a cross
        size=(2,2),  # Size of the cross (width and height)
        lineWidth=1,  # Line thickness
        lineColor='black',  # Line color (white)
        fillColor='black',  # Fill color (white)
        units='cm',  # Use normalized units
        pos=(0, 0)  # Center of the screen
        )
    photo_rect_off.draw()
    win.flip()
    return photo_rect_on, photo_rect_off, cross

def setup_free_convo_stimuli(win, photo_pos=(1, 0)):

    # Photodiode rectangle init
    size = 0.1
    photo_rect_on = visual.Rect(
        win=win, name='photo_rect_on',
        width=size * (9 / 16), height=size, units='norm',
        ori=0.0, pos=photo_pos, anchor='bottom-right',
        lineWidth=1.0, colorSpace='rgb', lineColor='white', fillColor='white',
        opacity=None, depth=0.0, interpolate=True)

    size = 0.1
    photo_rect_off = visual.Rect(
        win=win, name='photo_rect_off',
        width=size * (9 / 16), height=size, units='norm',
        ori=0.0, pos=photo_pos, anchor='bottom-right',
        lineWidth=1.0, colorSpace='rgb', lineColor='black', fillColor='black',
        opacity=None, depth=0.0, interpolate=True)


    photo_rect_off.draw()
    win.flip()
    return photo_rect_on, photo_rect_off