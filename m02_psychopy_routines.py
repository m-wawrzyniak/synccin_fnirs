"""
Contains full PsychoPy-like procedures used during procedure e.g. movie stimulus routine or free conversation routine.
"""

from psychopy.constants import (NOT_STARTED, STARTED, PLAYING, PAUSED,
                                STOPPED, FINISHED, PRESSED, RELEASED, FOREVER)
from psychopy import visual, core, event, sound

from config import FRAME_TOLERANCE

def interrupt(msg, win, keys=('x',), timeout=None):
    """
    Displays a message in a PsychoPy window and waits for one of the specified keys.

    Args:
        msg (str): message displayed to the Researcher
        win (Window): PsychoPy window at which message should be displayed
        keys (tuple): Keyboard keys which will finish the interruption.
        timeout (float): Time after auto-continue will occur.
    """
    print(msg)  # log to console

    # prepare the message
    message = visual.TextStim(win, text=msg, color='white', wrapWidth=1.5)
    message.draw()
    win.flip()

    # wait for key press or timeout
    if timeout is not None:
        timer = core.Clock()
        while timer.getTime() < timeout:
            these_keys = event.getKeys(keyList=keys)
            if these_keys:
                break
            core.wait(0.05)
    else:
        event.clearEvents()
        _ = event.waitKeys(keyList=keys)

    win.flip()
    core.wait(0.1)  # short pause to avoid visual artifacts

def setup_routine_components(components):
    """
    Initialize PsychoPy routine components.

    Args:
        components (list): List of PsychoPy components, which will be prepared for the presentation.
    """
    for comp in components:
        comp.tStart = None
        comp.tStop = None
        comp.tStartRefresh = None
        comp.tStopRefresh = None
        if hasattr(comp, 'status'):
            comp.status = NOT_STARTED

def run_routine(win, routine_components, routine_timer, defaultKeyboard, msg='Running routine...', duration=None, escape_key="escape"):
    """
    Using specific window 'win' (psychopy.visual.Window), creates routine segment with routine_componentes (list of PsychoPy stimuli) and runs it.

    Args:
        win (psychopy.visual.Window): Dyad window at which routine will be presented.
        routine_components (list): List of PsychoPy components utilized during the routine.
        routine_timer (psychopy.core.Clock): Internal PsychoPy Clock
        defaultKeyboard (psychopy.keyboard.Keyboard): Keyboard used for User interface.
        msg (str): Message printed when run.
        duration (int|None): How long routine will be run
        escape_key (str): String representation of the key which can be used to leave the routine.
    """
    print(msg)

    # setup timers and fram counters
    continue_routine = True
    frameN = -1
    routine_timer.reset()
    _timeToFirstFrame = win.getFutureFlipTime(clock="now")

    while continue_routine:
        # update time and frames
        t = routine_timer.getTime()
        tThisFlip = win.getFutureFlipTime(clock=routine_timer)
        tThisFlipGlobal = win.getFutureFlipTime(clock=None)
        frameN += 1

        # update components
        for comp in routine_components:
            if comp.status == NOT_STARTED and tThisFlip >= 0.0 - FRAME_TOLERANCE:
                comp.frameNStart = frameN
                comp.tStart = t
                comp.tStartRefresh = tThisFlipGlobal
                win.timeOnFlip(comp, 'tStartRefresh')
                comp.setAutoDraw(True)

            if comp.status == STARTED and duration and tThisFlipGlobal > comp.tStartRefresh + duration - FRAME_TOLERANCE:
                comp.tStop = t
                comp.frameNStop = frameN
                comp.setAutoDraw(False)

        # check for quit
        if defaultKeyboard.getKeys(keyList=[escape_key]):
            core.quit()

        # check if all components finished
        continue_routine = any(
            hasattr(comp, "status") and comp.status == STARTED for comp in routine_components
        )

        # update screeen
        if continue_routine:
            win.flip()

    # autodraw cleanup
    for comp in routine_components:
        if hasattr(comp, "setAutoDraw"):
            comp.setAutoDraw(False)

def run_stimulus_routine(win, mov_name, movie, photo_rect_on, photo_rect_off, routineTimer, thisExp, defaultKeyboard,
                         movie_duration=None):
    """
    Using specific window 'win' (psychopy.visual.Window), creates routine segment used during movie presentation: movies, photodiode marker and fixation cross.

    Args:
        win (Window): PsychoPy Window at which stimulus will be presented (Subjects window)
        mov_name (str): Movie ID / movie name.
        movie (MovieStim): Movie object which will be played.
        photo_rect_on (visual.Rect): Photodiode '1' signal box (white).
        photo_rect_off (visual.Rect): Photodiode '0' signal box (black).
        routineTimer (psychopy.core.Clock): Internal PsychoPy Clock
        thisExp (dict): PsychoPy log dictionary.
        defaultKeyboard (psychopy.keyboard.Keyboard): Keyboard used for UI
        movie_duration (int|None): Optional length of the movie presentation. If None, full length will be played.

    """
    # Set clocks, frames etc.
    continueRoutine = True
    t = 0
    frameN = -1
    routineTimer.reset()
    _timeToFirstFrame = win.getFutureFlipTime(clock="now")
    if movie_duration is None:
        movie_duration = movie.duration

    # photodiode toogle setup
    photo_rect_duration = movie_duration
    photo_toggle_time = 0.5
    last_toggle_time = 0
    toggle_cnt = 0
    movie_id = int(mov_name[-1])
    photo_is_on = False

    # routine loop
    while continueRoutine:
        # update time and frame count
        t = routineTimer.getTime()
        tThisFlip = win.getFutureFlipTime(clock=routineTimer)
        tThisFlipGlobal = win.getFutureFlipTime(clock=None)
        frameN = frameN + 1  # number of completed frames (so 0 is the first frame)

        # update components on each frame
        if movie.status == NOT_STARTED and tThisFlip >= 0.0 - FRAME_TOLERANCE:
            # keep track of start time/frame for later
            movie.frameNStart = frameN  # exact frame index
            movie.tStart = t  # local t and not account for scr refresh
            movie.tStartRefresh = tThisFlipGlobal  # on global time
            win.timeOnFlip(movie, 'tStartRefresh')  # time at next scr refresh
            # add timestamp to datafile
            thisExp.timestampOnFlip(win, '{}.started'.format(mov_name))
            movie.setAutoDraw(True)
        if movie.status == STARTED:
            # check whether to stop the routine
            if tThisFlipGlobal > movie.tStartRefresh + movie_duration - FRAME_TOLERANCE:
                movie.tStop = t
                movie.frameNStop = frameN
                thisExp.timestampOnFlip(win, '{}.stopped'.format(mov_name))
                movie.setAutoDraw(False)

        # toggling photodiode box for communication: based on movie id.
        if (tThisFlipGlobal >= last_toggle_time + photo_toggle_time) and (toggle_cnt <= movie_id * 2):
            last_toggle_time = tThisFlipGlobal
            if not photo_is_on:
                photo_rect_on.setAutoDraw(True)
                photo_rect_off.setAutoDraw(False)
            else:
                photo_rect_on.setAutoDraw(False)
                photo_rect_off.setAutoDraw(True)
            photo_is_on = not photo_is_on
            toggle_cnt += 1

        # check for quit
        if defaultKeyboard.getKeys(keyList=["escape"]):
            core.quit()

        # check if all components have finished
        if not continueRoutine:  # flag forced break
            break
        continueRoutine = False  # assume all components finished
        for thisComponent in [movie]:
            if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                continueRoutine = True  # if at least one component is still not finished, revert the flag
                break

        # refresh the screen
        if continueRoutine:
            win.flip()

    # cleanup
    print('{} finished'.format(mov_name))
    for thisComponent in [movie]:
        if hasattr(thisComponent, "setAutoDraw"):
            thisComponent.setAutoDraw(False)
    movie.stop()
    routineTimer.reset()
    photo_rect_on.setAutoDraw(False)
    photo_rect_off.setAutoDraw(True)

def run_free_convo_routine(win, win_master, photo_rect_on, photo_rect_off,
                           convo_countdown, convo_len, routineTimer):
    """
    Using specific window 'win' (psychopy.visual.Window), creates routine segment used during free conversation:
    photodiode marker, audio signal and Researcher countdown.

    Args:
        win (Window): PsychoPy window presented to Dyad.
        win_master (Window): PsychoPy window presented to the Researcher.
        photo_rect_on (visual.Rect): Photodiode '1' signal box (white).
        photo_rect_off (visual.Rect): Photodiode '0' signal box (black).
        convo_countdown (float): Countdown length prior to free conversation.
        convo_len (float): Conversation length.
        routineTimer (Clock): PsychoPy clock.

    """
    # timer and frame setup
    routineTimer.reset()
    frameN = -1
    _timeToFirstFrame = win.getFutureFlipTime(clock="now")

    # countdown text setup
    countdown_text = visual.TextStim(win_master, text="", height=0.1, color='white', pos=(0, 0))

    # phase 0: countdown
    wait_timer = core.Clock()
    response = _show_countdown(convo_countdown, win_master, wait_timer, countdown_text, "Countdown. Time left:")
    if response == "x":  # if pressed x, finish earlier
        return

    # phase 1: photodiode communication for convo start & audio signal
    photo_toggle_time = 1  # in seconds
    toggle_cnt = 0
    max_toggles = 4  # 2 full toggles (on/off)
    photo_is_on = False
    last_toggle_time = 0

    # toggling loop
    routineTimer.reset()
    continueRoutine = True
    while continueRoutine:
        t = routineTimer.getTime()
        tThisFlip = win.getFutureFlipTime(clock=routineTimer)
        frameN += 1

        if toggle_cnt < max_toggles and t >= last_toggle_time + photo_toggle_time:
            last_toggle_time = t
            if not photo_is_on:
                photo_rect_on.setAutoDraw(True)
                photo_rect_off.setAutoDraw(False)
            else:
                photo_rect_on.setAutoDraw(False)
                photo_rect_off.setAutoDraw(True)
            photo_is_on = not photo_is_on
            toggle_cnt += 1

        if toggle_cnt >= max_toggles:
            continueRoutine = False

        win.flip()

    photo_rect_on.setAutoDraw(False)
    photo_rect_off.setAutoDraw(True)

    # sound signal for the Dyad
    beep = sound.Sound("C", secs=1.0, stereo=True)
    beep.play()

    # phase 2: free conversation period
    wait_timer = core.Clock()
    response = _show_countdown(convo_len, win_master, wait_timer, countdown_text, 'Unrestricted conversation. Time left:')
    if response == "x":  # if pressed x, finish earlier
        pass

    # phase 3: photodiode communication for convo stop & audio signal
    beep = sound.Sound("C", secs=1.0, stereo=True)
    beep.play()

    routineTimer.reset()
    toggle_cnt = 0
    last_toggle_time = 0
    photo_is_on = False
    continueRoutine = True
    while continueRoutine:
        t = routineTimer.getTime()
        frameN += 1

        if toggle_cnt < max_toggles and t >= last_toggle_time + photo_toggle_time:
            last_toggle_time = t
            if not photo_is_on:
                photo_rect_on.setAutoDraw(True)
                photo_rect_off.setAutoDraw(False)
            else:
                photo_rect_on.setAutoDraw(False)
                photo_rect_off.setAutoDraw(True)
            photo_is_on = not photo_is_on
            toggle_cnt += 1

        if toggle_cnt >= max_toggles:
            continueRoutine = False

        win.flip()

    photo_rect_on.setAutoDraw(False)
    photo_rect_off.setAutoDraw(True)
    routineTimer.reset()

def _show_countdown(duration, win, timer, text_stim, text_content, key_list=("escape")):
    """
    Helper function for presenting the countdown counter to the Researcher.

    Args:
        duration (float): Total duration of countdown.
        win (Window): Window at which the countdown counter will be presented.
        timer (Timer): PsychoPy Timer object.
        text_stim (TextStim): Counter TextStim object.
        text_content (str): Counter content.
        key_list (list): Faster routine break keys.

    Returns:
        "x" | None
    """

    timer.reset()
    while timer.getTime() < duration:
        remaining = int(duration - timer.getTime())
        text_stim.text = f"{text_content}: {remaining} s"
        text_stim.draw()
        win.flip()

        keys = event.getKeys(keyList=key_list)
        if "escape" in keys:
            core.quit()
        elif "x" in keys:
            return "x"
    return None