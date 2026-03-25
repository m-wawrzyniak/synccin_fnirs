# %%
import numpy as np
import os
import pyphysio as ph
import pyphysio.artefacts as artefacts
from pyphysio.specialized.fnirs import Raw2OD, OD2Oxy, PCAFilter
from pyphysio.loaders import load_xrnirs, SDto1darray
from pyphysio.filters import IIRFilter
#%% 
from local_config import importeddir, processeddir
from config import members, sessions

print('02_process.py - v0.1')
print(ph.__version__)

#%%
dataset = 'W'
modality = 'FNIRS'

#%%
dyads = os.listdir(os.path.join(importeddir, dataset, modality))
for dyad in dyads:
    for member in members:
        for session in sessions:
            try:
                member_code = 'cg' if member == 'caregiver' else 'ch'
                datafilename = f'{dyad}_{modality}_{member_code}_{session}.nc'
                datafile = os.path.join(importeddir, dataset, modality, dyad, member, datafilename)
                nirs = load_xrnirs(datafile)

                #% skip SQ
                # we process all channels, we can filter them out later based on the SQ metrics
                # or use robust statistics that are not affected by outliers
                # or other approaches... let's catch this lates in the pipeline
                nirs.attrs['good_channels'] = np.arange(nirs.sizes['channel'])

                #%
                # convert to OD
                nirs = Raw2OD()(nirs)

                #remove MA with splines
                MA = artefacts.DetectMA(fuse='component')(nirs)
                nirs['MA'] = MA
                nirs = artefacts.MARA()(nirs)
                nirs = nirs.drop_vars('MA')

                #remove MA with wavelet
                nirs = artefacts.WaveletFilter()(nirs)

                #% convert to hb
                hb = OD2Oxy()(nirs)

                #% Zhang et al 2005
                hb = PCAFilter()(hb)

                #% bandpass filter
                hb = IIRFilter([0.01, 0.2], btype='bandpass')(hb)

                #% save the preprocessed data
                # I would call the folder 'hb' but we can discuss this together
                # filename currently uses the usual convention.
                #SDto1darray is to convert the SD info in the attributes to a valid format
                # for saving in netcdf
                outputdir = f'{processeddir}/{dataset}/HB/{dyad}/{member}'
                os.makedirs(outputdir, exist_ok=True)
                SDto1darray(hb).to_netcdf(os.path.join(outputdir, f'{dyad}_HB_{member_code}_{session}.nc'))
            except:
                print(f'Error processing {dyad} {member} {session}')

# %%
