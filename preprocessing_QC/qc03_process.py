# %%
"""
Relates 03_process.py
This was changed minimistically, to resemble Andrea's 03_process.py
"""

import numpy as np
import os
import pyphysio as ph
import pyphysio.artefacts as artefacts
from pyphysio.specialized.fnirs import Raw2OD, OD2Oxy, PCAFilter
from pyphysio.loaders import load_snirf, SDto1darray
from pyphysio.filters import IIRFilter
from datetime import datetime
import logging

#%%
from local_config import importeddir, processeddir
from config import members, sessions


print(ph.__version__)

log_date = datetime.now().strftime("%Y-%m-%d")
log_filename = f"qc03_process_{log_date}.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_filename), # Saves to file
        logging.StreamHandler()            # Still prints to console
    ]
)

logger = logging.getLogger(__name__)

#%%
dataset = 'W'
modality = 'FNIRS'
save_db = 'HB'

#%%
dyads = os.listdir(os.path.join(importeddir, dataset, modality))
logger.info(f"Starting processing run. PyPhysio version: {ph.__version__}")

for dyad in dyads:
    for member in members:
        for session in sessions:
            try:
                member_code = 'cg' if member == 'caregiver' else 'ch'
                datafilename = f'{dyad}_{modality}_{member_code}_{session}.snirf'
                datafile = os.path.join(importeddir, dataset, modality, dyad, member, datafilename)

                if not os.path.exists(datafile):
                    logger.warning(f"File missing: {datafile}")
                    continue

                # Load - Using 3-value unpack for refactor branch
                nirs, _, _ = load_snirf(datafile)

                # Prevent log(0)
                nirs.values = np.where(nirs.values <= 0, 1e-6, nirs.values)

                # QC / Processing steps
                nirs.attrs['good_channels'] = np.arange(nirs.sizes['channel'])
                nirs = Raw2OD()(nirs)

                # MA Removal
                MA = artefacts.DetectMA(fuse='component')(nirs)
                nirs['MA'] = MA
                nirs = artefacts.MARA()(nirs)
                nirs = nirs.drop_vars('MA')
                nirs = artefacts.WaveletFilter()(nirs)

                # HB Conversion & Filters
                hb = OD2Oxy()(nirs)
                hb = PCAFilter()(hb)
                hb = IIRFilter([0.01, 0.2], btype='bandpass')(hb)

                # Save
                outputdir = os.path.join(processeddir, dataset, save_db, dyad, member)
                os.makedirs(outputdir, exist_ok=True)
                output_file = os.path.join(outputdir, f'{dyad}_{save_db}_{member_code}_{session}.nc')
                SDto1darray(hb).to_netcdf(output_file)

                logger.info(f"PROCESSED: {dyad} | {member} | {session}")

            except Exception as e:
                logger.error(f"FAILED: {dyad} | {member} | {session} - Error: {str(e)}")

logger.info("Processing run completed.")