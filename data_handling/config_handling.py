ROOT = "E://SYNCC_IN//FNIRS//"
# ROOT = "/media/mateusz-wawrzyniak/ADATA SE880/DATA/FNIRS/fnirs_data_raw/"

# RAW DB
ROOT_RAW = f"{ROOT}fnirs_data_raw//"

SNIRF_DIR_CAREGIVER = f"{ROOT_RAW}matka"
SNIRF_DIR_CHILD = f"{ROOT_RAW}dziecko"

COMP_MERGED = f"{ROOT_RAW}meta_comp.csv"
STIM_TIME_FILE = f"{ROOT_RAW}meta_stim_time.csv"

MOVIE_MAP = {
    "1": "movie_brave",
    "3": "movie_peppa",
    "5": "movie_incredibles"
}

STIM_ORDER_FILE = f"{ROOT_RAW}meta_stim_order.csv"

OUTPUT_COMP_CAREGIVER = f"{ROOT_RAW}meta_comp_caregiver.csv"
OUTPUT_COMP_CHILD = f"{ROOT_RAW}meta_comp_child.csv"

OUTPUT_PATHS_CAREGIVER =  f"{ROOT_RAW}meta_paths_caregiver.csv"
OUTPUT_PATHS_CHILD =  f"{ROOT_RAW}meta_paths_child.csv"

# INTERNAL DB
OUTPUT_INTERNAL_DB = f"{ROOT}fnirs_data_internal_format//"

# EXTERNAL DB
'''
data/ UNIWAW_imported/ <MODALITY>/ <DYAD_ID>/ <member_folder>/
data/UNIWAW_imported/EEG/W_030/child/W_030_EEG_ch_Peppa.nc

https://github.com/SYNCC-IN/hyperscanning-signal-analysis/blob/main/docs/export_ncdf_guide.md

additional metadata abt the experiment and not the registration itself.

TODO: 2-sec pre-stim and post-stim
TODO: check if you got 2-sec post-stim for the last mov
t=0 at is at the first stim


TODO: remind Andrea to provide the scripts AT MONDAY, check on GitLab
TODO: remind Agnieszka when you are going to to QC and preproc

https://gitlab.com/a.bizzego/synccin

'''
EXTERNAL_STRUCTURE = {
    "root": {
        "format": lambda d_id: f"{ROOT}fnirs_data_external_format//",
        "dyad": {
            "format": lambda d_id: f"{d_id}",
            "modality": {
                "format": lambda d_id: "fnirs",
                "child_dir":{
                    "format": lambda d_id: f"{d_id}_child",
                    "movie_brave": {
                        "format": lambda d_id: f"{d_id}_child_Brave.snirf"},
                    "movie_peppa": {
                        "format": lambda d_id: f"{d_id}_child_Peppa.snirf"},
                    "movie_incredibles": {
                        "format": lambda d_id: f"{d_id}_child_Incredibles.snirf"},
                    "fc1": {
                        "format": lambda d_id: f"{d_id}_child_fc1.snirf"},
                    "fc2": {
                        "format": lambda d_id: f"{d_id}_child_fc2.snirf"}
                },
                "caregiver_dir":{
                    "format": lambda d_id: f"{d_id}_caregiver",
                    "movie_brave": {
                        "format": lambda d_id: f"{d_id}_caregiver_Brave.snirf"},
                    "movie_peppa": {
                        "format": lambda d_id: f"{d_id}_caregiver_Peppa.snirf"},
                    "movie_incredibles": {
                        "format": lambda d_id: f"{d_id}_caregiver_Incredibles.snirf"},
                    "fc1": {
                        "format": lambda d_id: f"{d_id}_caregiver_fc1.snirf"},
                    "fc2": {
                        "format": lambda d_id: f"{d_id}_caregiver_fc2.snirf"}
                }
            }
        }
    }
}

SNIRF_GOAL_STRUCTURE = {
    "aux1": True, # adjust: time, dataTimeSeries
    "aux2": True, # adjust: time, dataTimeSeries
    "aux3": True, # adjust: time, dataTimeSeries
    "aux4": True, # adjust: time, dataTimeSeries
    "aux5": True, # adjust: time, dataTimeSeries
    "aux6": True, # adjust: time, dataTimeSeries
    "data1": True, # adjust: time, dataTimeSeries
    "metaDataTags": True, # adjust: device_timestamp, first_timestamp, missing_sample, sample_index, sync_point(?)
    "probe": True
}