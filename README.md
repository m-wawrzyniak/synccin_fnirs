# SYNCC-IN fNIRS + EKG Procedure

This repository contains research software for running a **multimodal registration paradigm** involving **child–parent dyads**, combining **functional near-infrared spectroscopy (fNIRS)** with **electrocardiography (EKG)**.  
Developed within the **SYNCC-IN project** (University of Warsaw).

The system integrates:  
- **Two CortiVision Spectrum C23 fNIRS amplifiers** (child and parent)  
- **Dual fNIRS recording control** via CortiView software  
- **EKG recording** 
- **Stimulus presentation** (Pixar movie clips)
- **Unrestricted conversation** (Between the child and parent)
- **Custom experiment control and logging** (PsychoPy GUI + command-line interface)  

---

## Overview

The paradigm is divided into two main phases:  

1. **Main stimulation**
   - Randomized presentation of three short Pixar movie clips (~60 s each)  
   - Automatic start/stop markers sent to both fNIRS devices  
   - Photodiode used as digital marker signalization for EKG synchronization  

2. **Unrestricted conversation**  
   - Audio-cued free conversation between child and parent (two topics, 3 minutes each)  
   - Both fNIRS and EKG recordings continue throughout the interaction  

This design enables **precise temporal alignment** of multimodal signals (fNIRS, EKG, audio, and video) during naturalistic parent–child interaction.  

---

## Key Features

- **Multimodal synchronization**  
  - Dual fNIRS streams (child + parent)  
  - EKG acquisition for joint physiological recording  
  - Automatic event markers for video onsets and offsets  

- **Automated experiment flow**  
  - Randomized stimulus presentation order  
  - Controlled conversation blocks with countdowns and audio cues  
  - Automated start/stop control of recording phases  

- **Experiment control**  
  - Hybrid **command-line interface + PsychoPy GUI**  
  - Logging of pseudo-anonymous dyad codes  
  - Real-time procedure prompts for the experiment operator  
  - Communication with CortiView instances for event registration

---

## Requirements

- **Python**: 3.10  
- **Dependencies**: listed in `requirements.txt`  
- **Operating system**: Windows 10/11 
- **Hardware setup**:  
  - One Master PC (running the procedure script and GUI)  
  - Two CortiVision Spectrum C23 amplifiers and caps (child + parent)  
  - CortiView software installed and configured on both systems  
  - EKG amplifier with photodiode input used for signal synchronization
  - Executive monitor for stimulus presentation  

---

## Usage

The main entry point is:

```bash
run_procedure_fnirs.bat
```
This launches:
- The command-line interface
- The PsychoPy GUI for dyad ID input and phase control

---
## Procedure Outline

**Preparation**

1. Both fNIRS caps (child + parent) are fitted and calibrated manually using CortiView

2. Senior researcher and User ensure correct sensor placement and calibration quality

3. User confirms readiness signal from the senior researcher

**Main Stimulation**

1. Randomized presentation of three Pixar clips (~60 s each)

2. Start/stop markers sent to both fNIRS devices

3. Fixation cross (10 s) between clips

4. Recording stops after all three videos are presented

**Unrestricted Conversation**

1. Two conversation topics (3 minutes each)

2. 30-second countdown before each session (displayed on GUI)

3. Audio cues (C-note, 1 s) signal start and end of each conversation

4. Recording continues during both conversations

5. Procedure ends after the second topic

For the full, detailed timeline, see PARADIGM.md.

---

## Repository Structure

```bash
SYNCC-IN/
│
├── cortivision_info          # Basic information concerning Corivision comms.
├── legacy                    # Legacy code
├── config.py                 # Configuration and hyperparameters
├── experimental_scripts.py   # Experimental code
├── m01_procedure_setup.py    # Procedure setup, PsychoPy objects etc.
├── m02_psychopy_routines.py  # PsychoPy routines handling
├── m03_cortiview_comms.py    # CortiView communication handling
├── main_procedure.py         # Main executable script
├── PARADIGM.md               # Paradigm timeline
├── README.md                 # README
├── requirements.txt          # Python dependencies
└── run_procedure_fnirs.bat   # Windows entry point
```

---

## Attribution

Developed by Mateusz Wawrzyniak within the SYNCC-IN project, University of Warsaw.

This software is released under the MIT License.

Partner laboratories are welcome to reuse or adapt the codebase.