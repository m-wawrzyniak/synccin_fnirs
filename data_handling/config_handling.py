#ROOT = "E://SYNCC_IN//FNIRS//"
ROOT = "C://Users//user//Desktop//SYNCC-IN//FNIRS//"
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
https://github.com/SYNCC-IN/hyperscanning-signal-analysis/blob/main/docs/export_ncdf_guide.md

TODO: remind Andrea to provide the scripts AT MONDAY, check on GitLab
TODO: remind Agnieszka when you are going to to QC and preproc

!!! TODO: Didnt copy stim1 containers

https://gitlab.com/a.bizzego/synccin

'''

EXTERNAL_STRUCTURE = {
    "root": {
        "format": lambda d_id: f"{ROOT}UNIWAW_imported//",
        "modality": {
            "format": lambda d_id: "FNIRS",
            "dyad": {
                "format": lambda d_id: f"{d_id[0]}_{d_id[1:]}",
                "child_dir":{
                    "format": lambda d_id: f"child",
                    "movie_brave": {
                        "format": lambda d_id: f"{d_id[0]}_{d_id[1:]}_FNIRS_ch_Brave.snirf"},
                    "movie_peppa": {
                        "format": lambda d_id: f"{d_id[0]}_{d_id[1:]}_FNIRS_ch_Peppa.snirf"},
                    "movie_incredibles": {
                        "format": lambda d_id: f"{d_id[0]}_{d_id[1:]}_FNIRS_ch_Incredibles.snirf"},
                    "fc1": {
                        "format": lambda d_id: f"{d_id[0]}_{d_id[1:]}_FNIRS_ch_Talk1.snirf"},
                    "fc2": {
                        "format": lambda d_id: f"{d_id[0]}_{d_id[1:]}_FNIRS_ch_Talk2.snirf"}
                },
                "caregiver_dir":{
                    "format": lambda d_id: f"caregiver",
                    "movie_brave": {
                        "format": lambda d_id: f"{d_id[0]}_{d_id[1:]}_FNIRS_cg_Brave.snirf"},
                    "movie_peppa": {
                        "format": lambda d_id: f"{d_id[0]}_{d_id[1:]}_FNIRS_cg_Peppa.snirf"},
                    "movie_incredibles": {
                        "format": lambda d_id: f"{d_id[0]}_{d_id[1:]}_FNIRS_cg_Incredibles.snirf"},
                    "fc1": {
                        "format": lambda d_id: f"{d_id[0]}_{d_id[1:]}_FNIRS_cg_Talk1.snirf"},
                    "fc2": {
                        "format": lambda d_id: f"{d_id[0]}_{d_id[1:]}_FNIRS_cg_Talk2.snirf"}
                }
            }
        }
    }
}

SNIRF_BASE_STRUCTURE = {
    'formatVersion': 'str',
    'nirs': {
        "aux1": {
            'dataTimeSeries': 'array',
            'name': 'str',
            'time': 'array'
        },
        "aux2": {
            'dataTimeSeries': 'array',
            'name': 'str',
            'time': 'array'
        },
        "aux3": {
            'dataTimeSeries': 'array',
            'name': 'str',
            'time': 'array'
        },
        "aux4": {
            'dataTimeSeries': 'array',
            'name': 'str',
            'time': 'array'
        },
        "aux5": {
            'dataTimeSeries': 'array',
            'name': 'str',
            'time': 'array'
        },
        "aux6": {
            'dataTimeSeries': 'array',
            'name': 'str',
            'time': 'array'
        },
        "data1": {
            'dataTimeSeries': 'array',
            'measurementList_': 'dict',
            'time': 'array'
        },
        "metaDataTags": {
            'device_timestamp': 'array',
            'first_timestamp': 'float',
            'missing_sample': 'array',
            'sample_index': 'array',
            'other_': 'other'
        },
        "probe": 'dict',
        "stim1": {
            'data': 'array',
            'name': 'str'
        },
        "stim2": {
            'data': 'array',
            'name': 'str'
        },
        "stim3": {
            'data': 'array',
            'name': 'str'
        },
        "stim4": {
            'data': 'array',
            'name': 'str'
        },
        "stim5": {
            'data': 'array',
            'name': 'str'
        },
        "stim6": {
            'data': 'array',
            'name': 'str'
        },

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

PADDING = 2.00