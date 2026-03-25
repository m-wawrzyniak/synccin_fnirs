# %%
import numpy as np
import os
import pyphysio as ph
import pyphysio.artefacts as artefacts
from pyphysio.specialized.fnirs import Raw2OD, OD2Oxy, PCAFilter
from pyphysio.loaders import load_xrnirs, SDto1darray
from pyphysio.filters import Prewhitening
from pyphysio.utils import Wavelet
#%% 
from local_config import processeddir
from config import members, sessions, margin

print('04_compute_WC.py - v0.1')
print(ph.__version__)

#%%
dataset = 'W'

#%%
fresamp = 5
prew = Prewhitening(pmax=8)
wavelet_comp = Wavelet(freqs=np.arange(0.01, 0.21, 0.01)[::-1])

#%%
dyads = os.listdir(os.path.join(processeddir, dataset, 'HB'))
for dyad in dyads:
    for member in members:
        for session in sessions:
            try:
                member_code = 'cg' if member == 'caregiver' else 'ch'
                datafilename = f'{dyad}_HB_{member_code}_{session}.nc'
                datafile = os.path.join(processeddir, dataset, 'HB', dyad, member, datafilename)
                nirs = load_xrnirs(datafile)

                nirs = nirs.p.reset_times(-margin)
                nirs = nirs.p.resample(fresamp)
                
                #select only oxy
                nirs = nirs.isel({'component':[0]})
                
                nirs = prew(nirs) #should we do this? If yes, should we change the freqs of the wavelets?
                w = wavelet_comp(nirs)

                outputdir = f'{processeddir}/{dataset}/WC/{dyad}/{member}'
                os.makedirs(outputdir, exist_ok=True)
                SDto1darray(w).to_netcdf(os.path.join(outputdir, f'{dyad}_WC_{member_code}_{session}.nc'), auto_complex=True)
            except:
                print(f'Error processing {dyad} {member} {session}')
            
# %%
