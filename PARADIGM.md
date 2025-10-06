# SYNCC-IN fNIRS Procedure  
**University of Warsaw**  
**Date:** 06.10.2025  

This document describes the detailed procedure for running the **SYNCC-IN multimodal registration experiment**, involving child–parent dyads with **fNIRS** and **EKG** recordings.

---

## Roles and Components

| Term              | Description                                                                                  |
|-------------------|----------------------------------------------------------------------------------------------|
| **Master PC**     | Main computer running the procedure and scripts. Operated by the **User**.                   |
| **User**          | Researcher responsible for controlling the procedure at the Master PC and fNIRS calibration. |
| **Subjects**      | Child–parent dyad participating in the experiment.                                           |
| **Exec. Monitor** | Display where all stimuli (videos) are presented to the subjects.                            |
| **Main Videos**   | Pixar movie snippets used as primary stimuli.                                                |
| **Convo.**        | Unrestricted conversation between the child and the parent.                                  |

---

## Preparation

1. **Subject Setup**  
   - Both child and parent are prepared according to the **fNIRS environment preparation guidelines**.  
   - This includes initializing and calibrating both Child and Parent fNIRS systems in Cortiview and so it won't be explained in this document.

2. **Researcher Instructions**  
   - The **Senior Researcher** explains the video presentation procedure to the Subjects.  
   - Once both fNIRS devices are calibrated and ready, the senior researcher signals readiness to the **User**.

3. **Procedure Start**  
   - The User launches the experiment by executing:  
     ```
     run_procedure_fnirs.bat
     ```
   - This starts both the command-line interface (CLI) and a simplified PsychoPy GUI.

4. **Logging Setup**  
   - The User enters the required session information (e.g., pseudo-anonymous dyad code) in the PsychoPy GUI and confirms by pressing **OK**.

---

## Video Presentation Phase

1. **Recording Start**  
   - fNIRS recording begins on both devices.  
   - A fixation cross appears on the **Exec. Monitor**.

2. **Video Presentation Preparation**  
   - The order of the three video snippets is randomized (without replacement).  
   - The photodiode signaling display is prepared.  
   - The system waits for **User confirmation**.

3. **Stimulus Presentation Cycle**  
   - The fixation cross is removed.  
   - One of the main videos is selected and presented on the **Exec. Monitor**.  
   - A **marker** is sent to both Cortiview instances to indicate video onset (with movie ID).  
   - During the first 2–3 seconds, a **photodiode signal** marks the onset to the EEG amplifier.  
   - After approximately **60 seconds**, the video ends.  
   - A **marker** is sent again to indicate video offset.  
   - A **fixation cross** is displayed for*10 seconds between videos.

4. **Repetition**  
   - Steps above are repeated until **all three videos** have been presented.

5. **Post-Stimulation**  
   - Recording on both fNIRS devices stops.  
   - The script enters standby mode.  
   - The User informs the **Senior Researcher** that the movie presentation phase is complete.

---

## Unrestricted Conversation Phase

1. **Introduction**  
   - The **Senior Researcher** introduces the conversation topic to the subjects.  
   - When ready, the researcher signals to the User.

2. **Countdown**  
   - The User starts the conversation procedure; recording starts again on both fNIRS devices.  
   - A **30-second countdown** is shown on the PsychoPy GUI while the User and researcher leave the room.

3. **Conversation Period**  
   - After the countdown, a **1-second C-note audio cue** signals the start of conversation.  
   - The subjects converse freely for **180 seconds**.  
   - A second **audio cue** signals the end of the conversation.

4. **Post-Conversation**  
   - The User and Senior Researcher return to the room.  
   - fNIRS recording stops, and the script waits for User input.

5. **Repetition**  
   - Steps 1–4 are repeated for the **second conversation topic**.  
   - After completion, the script **shuts down all UI elements** and saves **data logs** to the predefined directory.

---

## End of Procedure

After data saving and UI shutdown, the experiment concludes.  
All logs are stored in the directory specified during the GUI setup.
