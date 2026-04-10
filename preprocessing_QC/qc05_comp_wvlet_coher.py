#%%
"""
This was changed minimistically, to resemble Andrea's 05_compute_wavelet_coherence.py
"""

import numpy as np
import os
import xarray as xr
import pandas as pd

import pyphysio as ph
from pyphysio.loaders import load_xrnirs
from pyphysio.compare import wavelet_coherence, compute_pairwise_similarity
from pyphysio.utils import Wavelet
wavelet_comp = Wavelet(freqs=np.arange(0.01, 0.21, 0.01)[::-1])

from local_config import processeddir, synchdir
from config import sessions, margin

import warnings
warnings.filterwarnings('ignore')

def load_wt(datafile):
    wt = load_xrnirs(datafile)
    wt = wt.p.reset_times(-margin)
    return wt

#%%
print('05_compute_wavelet_coherence.py - v0.1')
print(ph.__version__)

#%%
dataset = 'W'
fresamp = 5

#%%
dyads = np.sort(os.listdir(f'{processeddir}/{dataset}/WC'))

#%% process all sessions
results_all_sessions = []
for session in sessions:

    data_all = []
    for dyad in [dyads[0], dyads[0]]:
        filename_child = f'{dyad}_WC_ch_{session}.nc'
        filename_careg = f'{dyad}_WC_cg_{session}.nc'

        path_child = f'{processeddir}/{dataset}/WC/{dyad}/child'
        path_careg = f'{processeddir}/{dataset}/WC/{dyad}/caregiver'

        #check if both files are present
        try:
            child_present = filename_child in os.listdir(path_child)
            careg_present = filename_careg in os.listdir(path_careg)
        except:
            child_present = False
            careg_present = False

        #load files if both are present
        if child_present and careg_present:
            wt_child = load_wt(f'{path_child}/{filename_child}')
            wt_careg = load_wt(f'{path_careg}/{filename_careg}')

            wt_dyad = xr.concat([wt_child, wt_careg], dim='member', join='inner')
            wt_dyad['member'] = ['child', 'caregiver']
            data_all.append(wt_dyad)

    #concatenate all dyads for this session
    data_all_xr = xr.concat(data_all, dim='dyad')
    data_all_xr['dyad'] = dyads

    #%% for all channels
    results_all_channels = []
    for i_ch in data_all_xr['channel']:

        data_ch = data_all_xr.isel({'channel': i_ch, 'component': 0})

        wavelet_comp._compute_scales(data_all_xr)

        #the following function will compute wavelet coherence between relevant signals (true and surrogate)
        wc_channel = compute_pairwise_similarity(data_ch,
                                                metric_func=wavelet_coherence,
                                                intra_dim='member',
                                                inter_dim='dyad',
                                                skip_identity=True, #do not compute coherence between same member of same dyad
                                                skip_cross=False, #compute surrogates (e.g., child of dyad 1 vs caregiver of dyad 2)
                                                skip_same=True, #skip same member different dyad (e.g., child of dyad 1 vs child of dyad 2)
                                                wavelet_object=wavelet_comp,
                                                use_coi=True,
                                                return_WC=False)

        #results will be symmetrical caregiver <==> child = child <==> caregiver, so we drop duplicate rows
        wc_channel = wc_channel.query('member1 == "child"')
        wc_channel['channel'] = int(i_ch)

        results_all_channels.append(wc_channel)

    results_all_channels = pd.concat(results_all_channels, ignore_index=True)
    results_all_sessions.append(results_all_channels)

results_all_sessions = pd.concat(results_all_sessions, ignore_index=True)
results_all_sessions.to_csv(f'{synchdir}/{dataset}/wc_results_all_sessions.csv', index=False)