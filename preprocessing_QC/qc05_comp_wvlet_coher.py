# %%
import numpy as np
import os
import xarray as xr
import pandas as pd
import pyphysio as ph
from pyphysio.loaders import load_xrnirs
from pyphysio.compare import wavelet_coherence, compute_pairwise_similarity
from pyphysio.utils import Wavelet
from datetime import datetime
import logging

# --- CONFIG & PATHS ---
from local_config import processeddir, synchdir
from config import sessions, margin
import warnings

warnings.filterwarnings('ignore')

# --- LOGGING SETUP ---
log_date = datetime.now().strftime("%Y-%m-%d")
log_filename = f"qc05_comp_wvlet_coher_{log_date}.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_filename),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


# --- FUNCTIONS ---
def load_wt(datafile):
    wt = load_xrnirs(datafile)
    wt = wt.p.reset_times(-margin)
    return wt


# Setup wavelet
wavelet_comp = Wavelet(freqs=np.arange(0.01, 0.21, 0.01)[::-1])

# Output path
os.makedirs(os.path.join(synchdir, 'W'), exist_ok=True)
FINAL_OUTPUT_CSV = os.path.join(synchdir, 'W', 'wc_results_all_sessions.csv')

logger.info(f"Starting Wavelet Coherence. PyPhysio version: {ph.__version__}")

# %% Get dyad list
# Note: Searching in 'WC' as per your folder structure
dyad_source_dir = os.path.join(processeddir, 'W', 'WC')
if not os.path.exists(dyad_source_dir):
    logger.error(f"Source directory not found: {dyad_source_dir}")
    exit()

dyads = np.sort(os.listdir(dyad_source_dir))

# %% process sessions
for session in sessions:
    logger.info(f"BEGIN SESSION: {session}")

    data_all = []
    valid_dyads = []

    # 1. Load data for this session
    for dyad in dyads:
        filename_child = f'{dyad}_WC_ch_{session}.nc'
        filename_careg = f'{dyad}_WC_cg_{session}.nc'
        path_child = os.path.join(processeddir, 'W', 'WC', dyad, 'child')
        path_careg = os.path.join(processeddir, 'W', 'WC', dyad, 'caregiver')

        file_c = os.path.join(path_child, filename_child)
        file_cg = os.path.join(path_careg, filename_careg)

        if os.path.exists(file_c) and os.path.exists(file_cg):
            try:
                wt_child = load_wt(file_c)
                wt_careg = load_wt(file_cg)

                # Stack child and caregiver
                wt_dyad = xr.concat([wt_child, wt_careg], dim='member', join='inner')
                wt_dyad['member'] = ['child', 'caregiver']

                data_all.append(wt_dyad)
                valid_dyads.append(dyad)
            except Exception as e:
                logger.warning(f"Failed to load dyad {dyad}: {e}")

    if not data_all:
        logger.warning(f"No data for session {session}. Skipping.")
        continue

    # 2. Concatenate session data & APPLY CONTRIBUTOR FIXES
    try:
        # Initial concat
        data_all_xr = xr.concat(data_all, dim='dyad')
        data_all_xr['dyad'] = valid_dyads

        # CONTRIBUTOR FIX: Drop timepoints that are not present in all dyads (prevents NaNs)
        data_all_xr = data_all_xr.dropna(dim='time')

        # CONTRIBUTOR ASSERTION: Ensure data is clean before math
        assert np.sum(np.isnan(data_all_xr.values)) == 0, f"NaN values detected in {session} after alignment"

        logger.info(f"Alignment successful. {len(valid_dyads)} dyads ready.")

    except Exception as e:
        logger.error(f"Concatenation/Assertion failed for {session}: {e}")
        continue

    # 3. Process channels for this session
    for idx, i_ch in enumerate(data_all_xr['channel']):
        try:
            # Select component 0 (HbO)
            data_ch = data_all_xr.isel({'channel': i_ch, 'component': 0})
            wavelet_comp._compute_scales(data_ch)

            # Compute similarity
            wc_channel = compute_pairwise_similarity(
                data_ch,
                metric_func=wavelet_coherence,
                intra_dim='member',
                inter_dim='dyad',
                skip_identity=True,
                skip_cross=False,
                skip_same=True,
                wavelet_object=wavelet_comp,
                use_coi=True,
                return_WC=False
            )
            """
            print("\n" + "#" * 40)
            print(f"DEBUG: Session: {session} | Channel: {idx}")
            print(f"Columns returned: {wc_channel.columns.tolist()}")
            print("First 2 rows of data:")
            print(wc_channel.head(2))
            print("#" * 40 + "\n")
            """

            # Symmetrize and Label
            wc_channel = wc_channel.query('member1 == "child"')
            wc_channel['channel'] = int(i_ch)
            wc_channel['session'] = session

            # Calculate Mean Coherence for True Dyads for the log
            # (Where dyad1 matches dyad2)
            true_pairs = wc_channel[wc_channel['dyad1'] == wc_channel['dyad2']]
            mean_true_coh = true_pairs['metric_value'].mean()

            # --- INCREMENTAL SAVE ---
            file_exists = os.path.isfile(FINAL_OUTPUT_CSV)
            wc_channel.to_csv(FINAL_OUTPUT_CSV, mode='a', index=False, header=not file_exists)

            logger.info(f"SUCCESS: {session} | Ch {idx} | Mean True Coherence: {mean_true_coh:.4f}")

        except Exception as e:
            logger.error(f"MATH ERROR: {session} | Ch {idx} - {e}")

logger.info(f"Processing complete. Results saved to {FINAL_OUTPUT_CSV}")