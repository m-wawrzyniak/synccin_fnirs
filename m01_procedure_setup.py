"""
Setup for logging paths, screens, windows, PsychoPy handlers, Pupil Capture communication and presented stimuli.
"""

import os
import ast
import pyglet

from numpy.random import randint
from psychopy import sound, gui, visual, core, data, event, logging, clock, colors, layout, monitors
import psychopy.iohub as io
from psychopy.hardware import keyboard

from config import LOG_DIR, WIN_SIZES

def setup_path_log_psychopy():
    """
    Setup paths and logs for fNIRS procedure.

    Returns:
        - expInfo (dict) Dictionary of experiment information (name:value)
        - thisExp (ExperimentHandler)
        - logFile (LogFile)
        - filename (str) Absolute path for saving all data and logs.
    """
    os.makedirs(LOG_DIR, exist_ok=True)
    os.chdir(LOG_DIR)

    # exp session info
    psychopyVersion = '2024.2.4'
    expName = 'fnirs_syncc_in_procedure'
    expInfo = {
        'participant': f"{randint(0, 999999):06.0f}",
        'session': '001',
        'window background color': '[0.0, 0.0, 0.0]',
        'free conversation countdown': '30',
        'free conversation length': '180',
        'debug mode': ['False', 'True'],
        'start at stage': ['2. Calibration', '3. Movies', '4. Free convo']
    }
    print(f"Syncc-In fNIRS procedure, participant: {expInfo['participant']}")

    # diad info
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
    """
    Setup ups PsychoPy IO devices.

    Args:
        main_win (Window): PsychoPy window, presented to the Subjects.
        expInfo (dict): Dictionary of experiment information (name:value)

    Returns:
        defaultKeyBoard
    """
    ioConfig = {}
    ioConfig['Keyboard'] = dict(use_keymap='psychopy')
    ioServer = io.launchHubServer(window=main_win, **ioConfig)
    defaultKeyboard = keyboard.Keyboard(backend='iohub')
    ioSession = '1'
    if 'session' in expInfo:
        ioSession = str(expInfo['session'])

    return defaultKeyboard

def check_screen_id_assignment():
    """
    Makes sure that monitor configuration at Win level is correct.
    """
    screens = pyglet.canvas.get_display().get_screens()

    for i, screen in enumerate(screens):
        print(f"Screen {i}: {screen.width}x{screen.height}, x={screen.x}, y={screen.y}")
        if screen.width != WIN_SIZES[i][0] or screen.height != WIN_SIZES[i][1]:
            raise TypeError('Screen IDs are wrong.')

def setup_windows(win_id_master, win_id_main, expInfo):
    """
    Creates PsychoPy.Window objects used during the procedure.

    Args:
        win_id_master (int) : ID of the window presented on Master PC.
        win_id_main (int) : ID of the window presented Subject PC.
        expInfo (dict): Experimental info dictionary.

    Returns:
        win_main (Window): PsychoPy Window object presented on Subject PC.
        win_master (Window): PsychoPy Window object presented on Master PC.
        gigabyte_monitor (Monitor): PsychoPy Monitor object representing Subject monitor.
        test_monitor (Monitor): PsychoPy Monitor object representing Master monitor.
    """
    all_monitors = monitors.getAllMonitors()
    print(f"Available monitors: {all_monitors}")

    # subject monitor specs
    gigabyte_monitor = monitors.Monitor('GIGABYTE')
    gigabyte_monitor.setWidth(52.7)
    gigabyte_monitor.setSizePix([2560, 1440])
    gigabyte_monitor.setDistance(65)
    gigabyte_monitor.saveMon()

    # master monitor specs
    test_monitor = monitors.Monitor('testMonitor')
    test_monitor.setWidth(30.0)
    test_monitor.setSizePix([640, 480])
    test_monitor.setDistance(50)
    test_monitor.saveMon()

    bckgnd_clr_str = expInfo['window background color']
    try:
        background_clr = ast.literal_eval(bckgnd_clr_str)
    except:
        background_clr = None

    if background_clr is None:
        background_clr = [-1.0, -1.0, -1.0]

    win_main = visual.Window(
        size=[2560, 1440], fullscr=True, screen=win_id_main,
        winType='pyglet', allowStencil=False,
        monitor=gigabyte_monitor, color=background_clr, colorSpace='rgb',
        blendMode='avg', useFBO=True,
        units='norm', infoMsg='.')
    win_main.mouseVisible = True

    win_master = visual.Window(
        size=[640, 480], fullscr=False, screen=win_id_master,
        winType='pyglet', allowStencil=False,
        monitor=test_monitor, color=background_clr, colorSpace='rgb',
        blendMode='avg', useFBO=True,
        units='norm', infoMsg='.')
    print("Windows defined")

    return win_main, win_master, gigabyte_monitor, test_monitor

def create_cortiview_recording_name(expInfo):
    """
    Creates standardized recording name fed to Cortiview instances.

    Args:
        expInfo (dict): PsychoPy experimental info.

    Returns:
        cortiview_filename (str)

    """
    ses_date, ses_time = expInfo['date'][:-7].split('_')
    ses_date = ses_date.replace('-', '_')
    ses_time = ses_time.replace('h', '')
    cortiview_filename = f"{ses_date}_fnirs_{ses_time}_{expInfo['participant']}"

    return cortiview_filename

def setup_helper_stimuli(win, photo_pos):
    """
    Creates PsychoPy.visual objects used during the movie procedure: photodiode communication rectangle and fixation cross.

    Args:
        win (Window): Window at which stimulus should be presented.
        photo_pos (tuple): Normalized screen coordinates at which the photodiode communication rectangle will be presented.

    Returns:
        photo_rect_on (visual.Rect): White rectangle, used as '1' signal for photodiode.
        photo_rect_off (visual.Rect): Black rectangle, used as '0' signal for photodiode.
        cross (visual.ShapeStim): Fixation cross.
    """

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
        vertices='cross',
        size=(2,2),
        lineWidth=1,
        lineColor='black',
        fillColor='black',
        units='cm',
        pos=(0, 0)
        )
    photo_rect_off.draw()
    win.flip()
    return photo_rect_on, photo_rect_off, cross

def setup_free_convo_stimuli(win, photo_pos=(1, 0)):
    """
    Creates PsychoPy.visual objects used during the free conversation procedure: photodiode communication rectangle.

    Args:
        win (Window): Window at which stimulus should be presented.
        photo_pos (tuple): Normalized screen coordinates at which the photodiode communication rectangle will be presented.

    Returns:
        photo_rect_on (visual.Rect): White rectangle, used as '1' signal for photodiode.
        photo_rect_off (visual.Rect): Black rectangle, used as '0' signal for photodiode.
    """

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