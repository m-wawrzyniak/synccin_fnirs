"""
Relates to 02_screen_quality_window.py
This was adjusted for my own purpose.
Methodological choices made by Andrea.
"""
import os
import pandas as pd
import numpy as np

import pyphysio.filters as flt
import pyphysio.utils as utils
from pyphysio.specialized.fnirs import ScalpCouplingIndexCorrelation, ScalpCouplingIndexPower, Raw2OD
from pyphysio.sqi import SpectralPowerRatio, PercentageNAN

from pyphysio.loaders import load_snirf

import data_handling.config_handling as conf
from data_handling.external_format import _resolve_path
from data_handling.snirf_handling import create_meta_df, merge_meta


bpm_max = 150
bpm_min = 40
f_interval = 0.4
OUTPUT_CSV = "quality_results_window.csv"
wlength = 15


def run_quality_check():
    cgs_df, _ = create_meta_df(conf.SNIRF_DIR_CAREGIVER)
    cls_df, _ = create_meta_df(conf.SNIRF_DIR_CHILD)
    master_df = merge_meta(caregiver_df=cgs_df, child_df=cls_df)

    sessions = ["movie_brave", "movie_peppa", "movie_incredibles", "fc1", "fc2"]
    roles = ["child", "caregiver"]

    for _, row in master_df.iterrows():
        dyad_id = row["dyad_id"]

        for role in roles:
            for sess_key in sessions:
                try:
                    path_info = _resolve_path(dyad_id, conf.EXTERNAL_STRUCTURE, role=role, file_key=sess_key)
                    datafile = path_info["file_path"]

                    if not os.path.exists(datafile):
                        continue

                    # Load whole file first
                    nirs_full, _ = load_snirf(datafile, has_stim=True)

                    # --- WINDOWING LOGIC ---
                    t_start = nirs_full.p.get_start_time()
                    t_stop = nirs_full.p.get_end_time()

                    print(t_start, t_stop)

                    w_start = t_start
                    w_stop = t_start + wlength

                    while w_stop <= t_stop:
                        # Segment the signal for this window
                        nirs_window = nirs_full.p.segment_time(w_start, w_stop)

                        # --- QC Math on the Window ---
                        perc_nan = PercentageNAN([0, 5])(nirs_window).mean(dim=['component'])
                        nirs_window = nirs_window.p.process_na('impute')

                        f_max, f_min = bpm_max / 60, bpm_min / 60
                        nirs_cardiac = flt.IIRFilter([f_min, f_max])(nirs_window)

                        nirs_mean = nirs_cardiac.mean(dim=['component', 'channel'])
                        psd = utils.PSD('period')(nirs_mean)

                        f_peak = float(psd['freq'][np.argmax(psd.values.ravel())].values)
                        cardiac_band = [f_peak - f_interval / 2, f_peak + f_interval / 2]

                        cnr = SpectralPowerRatio([0, 1], method='period', bandN=cardiac_band, bandD=[f_min, f_max])(
                            nirs_cardiac.mean(dim=['component']))

                        sci_c = ScalpCouplingIndexCorrelation(cardiac_band=cardiac_band)(nirs_cardiac)
                        sci_p = ScalpCouplingIndexPower(cardiac_band=cardiac_band)(nirs_cardiac)

                        # --- Collect Window Chunk ---
                        session_results = []
                        for i_channel in range(nirs_window.sizes['channel']):
                            session_results.append({
                                'dyad': dyad_id,
                                'member': role,
                                'session': sess_key,
                                'f_card': f_peak,
                                'channel': i_channel,
                                'perc_nan': float(perc_nan.sel({'channel': i_channel, 'is_good': 0})),
                                'cnr': float(cnr.sel({'channel': i_channel, 'is_good': 0})),
                                'sci_c': float(sci_c.sel({'channel': i_channel, 'is_good': 0})),
                                'sci_p': float(sci_p.sel({'channel': i_channel, 'is_good': 0})),
                                't_start': w_start,
                                't_stop': w_stop
                            })

                        # Append window results to CSV
                        df_chunk = pd.DataFrame(session_results)
                        file_exists = os.path.isfile(OUTPUT_CSV)
                        df_chunk.to_csv(OUTPUT_CSV, mode='a', index=False, header=not file_exists)

                        # Slide the window
                        w_start += wlength
                        w_stop += wlength

                    print(f"Successfully processed all windows: {dyad_id} | {role} | {sess_key}")

                except Exception as e:
                    print(f"FAILED {dyad_id} | {role} | {sess_key}: {e}")


if __name__ == "__main__":
    # Clean start? Delete the old file if you want a fresh run
    # if os.path.exists(OUTPUT_CSV): os.remove(OUTPUT_CSV)
    run_quality_check()