import h5py
import pprint

import config_handling as conf
import snirf_handling as snirf
import external_format as ex

if __name__ == "__main__":

    ex._cut_movies(
        snirf_path="E:/SYNCC_IN/FNIRS/fnirs_data_raw/matka/2025_08_26_fnirs_1528_w050_m_movies_2025-08-26-15-28-49.snirf",
        stim_times=(-6.601205475012481,53.98954662499198,64.0883686249919,124.8270507249883,134.91860152499174,195.29113712498395),
        dyad_id="W050",
        is_child=False,
        external_structure=conf.EXTERNAL_STRUCTURE,
        snirf_goal_structure=conf.SNIRF_GOAL_STRUCTURE
    )

    with h5py.File("E://SYNCC_IN//FNIRS//fnirs_data_external_format//W050//fnirs//W050_caregiver//W050_caregiver_Incredibles.snirf", "r") as out_f:
        snirf_res = snirf.h5_to_dict(out_f)
        pprint.pprint(snirf_res)