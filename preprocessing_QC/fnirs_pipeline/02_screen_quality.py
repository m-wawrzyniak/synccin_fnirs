import pyphysio as ph
import pyphysio.filters as flt
import pyphysio.utils as utils
from pyphysio.specialized.fnirs import ScalpCouplingIndexCorrelation, ScalpCouplingIndexPower, Raw2OD
from pyphysio.sqi import SpectralPowerRatio, PercentageNAN

from pyphysio.loaders import load_xrnirs

import os
import numpy as np
import pandas as pd
from local_config import importeddir, signalqualitydir
from config import members, sessions

bpm_max = 150
bpm_min = 40
f_interval = 0.4

print('02_screen_quality.py - v0.2')
print(ph.__version__)

#%%
dataset = 'W'
modality = 'FNIRS'

#%%
summary = []

# ideally there will be a function that returns an iterator of all files
# for now we just create some nested loops

dyads = os.listdir(os.path.join(importeddir, dataset, modality))
for dyad in dyads:
    for member in members:
        for session in sessions:
            try:
                member_code = 'cg' if member == 'caregiver' else 'ch'
                datafilename = f'{dyad}_{modality}_{member_code}_{session}.nc'
                datafile = os.path.join(importeddir, dataset, modality, dyad, member, datafilename)
                nirs = load_xrnirs(datafile)
                
                #check nans
                perc_nan = PercentageNAN([0, 5])(nirs)
                perc_nan = perc_nan.mean(dim=['component'])

                #impute nans
                nirs = nirs.p.process_na('impute')
                
                # filter and keep only cardiac band
                f_max = bpm_max/60
                f_min = bpm_min/60
                
                nirs_cardiac = flt.IIRFilter([f_min, f_max])(nirs)
                
                ## Estimate cardiac frequency
                ### Average channels
                nirs_mean = nirs_cardiac.mean(dim=['component', 'channel'])
                
                ### Compute spectrum
                psd = utils.PSD('period')(nirs_mean)
                
                ### Obtain peak freq
                f_peak = float(psd['freq'][np.argmax(psd.values.ravel())].values)
                
                ### Compute cardiac band
                cardiac_band = [f_peak-f_interval/2, f_peak+f_interval/2]
                
                # compute cardiac component / noise ratio based on spectrum
                cnr = SpectralPowerRatio([0, 1], method='period',
                                         bandN=cardiac_band, bandD=[f_min, f_max])(nirs_cardiac.mean(dim=['component']))
                
                sci_c = ScalpCouplingIndexCorrelation(cardiac_band=cardiac_band)(nirs_cardiac)
                sci_p = ScalpCouplingIndexPower(cardiac_band=cardiac_band)(nirs_cardiac)
                
                for i_channel in range(nirs.sizes['channel']):
                    perc_nan_ = float(perc_nan.sel({'channel': i_channel,
                                                    'is_good': 0}))
                    cnr_ = float(cnr.sel({'channel': i_channel,
                                            'is_good': 0}))
                    sci_c_ = float(sci_c.sel({'channel': i_channel,
                                                'is_good':0}))
                    sci_p_ = float(sci_p.sel({'channel': i_channel,
                                                'is_good':0}))
                    
                    summary.append({'dyad': dyad,
                                    'member': member,
                                    'session': session,
                                    'f_card': f_peak,
                                    'channel': i_channel,
                                    'perc_nan': perc_nan_,
                                    'cnr': cnr_,
                                    'sci_c': sci_c_,
                                    'sci_p': sci_p_})
            except Exception as e:
                print(dyad, member, session, e)

#%%
summary = pd.DataFrame(summary)

os.makedirs(os.path.join(signalqualitydir, dataset, modality), exist_ok=True)
summary.to_csv(os.path.join(signalqualitydir, dataset, modality, 'summary_fnirs_quality.csv'))
