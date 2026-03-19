import os
import pandas as pd
import h5py
import numpy as np
import shutil

import snirf_handling as snirf
import config_handling as conf

def create_struct_skeleton(comp_merged, external_structure):
    """
    Creates directory structure based on EXTERNAL_STRUCTURE config.

    Only creates folders (no files), up to:
    - child_dir
    - caregiver_dir

    :param comp_merged
    :param external_structure: config dict
    """
    comp_merged = pd.read_csv(comp_merged)
    root_format = external_structure["root"]["format"]
    dyad_struct = external_structure["root"]["dyad"]

    for dyad_id in comp_merged["dyad_id"].unique():

        # --- ROOT ---
        root_path = root_format(dyad_id)

        # --- DYAD ---
        dyad_path = os.path.join(
            root_path,
            dyad_struct["format"](dyad_id)
        )

        # --- MODALITY ---
        modality_struct = dyad_struct["modality"]
        modality_path = os.path.join(
            dyad_path,
            modality_struct["format"](dyad_id)
        )

        # --- CHILD DIR ---
        child_struct = modality_struct["child_dir"]
        child_path = os.path.join(
            modality_path,
            child_struct["format"](dyad_id)
        )

        # --- CAREGIVER DIR ---
        care_struct = modality_struct["caregiver_dir"]
        care_path = os.path.join(
            modality_path,
            care_struct["format"](dyad_id)
        )

        # create directories
        os.makedirs(child_path, exist_ok=True)
        os.makedirs(care_path, exist_ok=True)

    print("Structure skeleton created successfully.")


def _adjust_time(time_array, t_start, t_end):
    """
    Returns:
    - adjusted time (rebased)
    - indices to keep
    """
    mask = (time_array >= t_start) & (time_array <= t_end)

    if not np.any(mask):
        return None, None

    indices = np.where(mask)[0]
    new_time = time_array[indices]
    new_time = new_time - new_time[0]

    return new_time, indices


def _adjust_dataTimeSeries(data, indices):
    """
    Uses indices from _adjust_time
    """
    if indices is None:
        return None

    return data[indices]


def _adjust_metaDataTags(meta, indices, original_time):
    """
    Adjusts metaDataTags according to kept indices.

    Rules:
    - missing_sample → subset
    - sample_index → subset
    - device_timestamp → subset (no offset)
    - first_timestamp → subtract time_offset
    """

    if meta is None or indices is None:
        return None

    adjusted = {}

    # compute offset from ORIGINAL time
    time_offset = original_time[indices][0]

    # --- missing_sample ---
    if "missing_sample" in meta:
        arr = meta["missing_sample"]
        if isinstance(arr, np.ndarray) and len(arr) >= np.max(indices) + 1:
            adjusted["missing_sample"] = arr[indices]

    # --- sample_index ---
    if "sample_index" in meta:
        arr = meta["sample_index"]
        if isinstance(arr, np.ndarray) and len(arr) >= np.max(indices) + 1:
            adjusted["sample_index"] = arr[indices]

    # --- device_timestamp ---
    if "device_timestamp" in meta:
        arr = meta["device_timestamp"]
        if isinstance(arr, np.ndarray) and len(arr) >= np.max(indices) + 1:
            adjusted["device_timestamp"] = arr[indices]

    # --- first_timestamp ---
    if "first_timestamp" in meta:
        val = meta["first_timestamp"]
        if isinstance(val, (float, np.floating)):
            adjusted["first_timestamp"] = val + time_offset

    return adjusted


def _check_overlap(segments):
    intervals = list(segments.values())

    for i in range(len(intervals)):
        for j in range(i + 1, len(intervals)):
            a_start, a_end = intervals[i]
            b_start, b_end = intervals[j]

            if max(a_start, b_start) < min(a_end, b_end):
                print("Warning: overlapping movie segments detected")


def _safe_write_dataset(group, key, value):

    if isinstance(value, dict):
        subgrp = group.create_group(key)
        for k, v in value.items():
            _safe_write_dataset(subgrp, k, v)
        return

    # -----------------------------
    # FORCE unicode-safe conversion
    # -----------------------------
    if isinstance(value, np.ndarray):

        if value.dtype.kind in {"U", "O"}:
            value = np.array([str(x) for x in value.flatten()], dtype="S")

    elif isinstance(value, list):

        # detect string list
        if len(value) > 0 and isinstance(value[0], str):
            value = np.array([x.encode("utf-8") for x in value], dtype="S")
        else:
            try:
                value = np.array(value)
            except Exception:
                value = np.array(str(value), dtype="S")

    elif isinstance(value, str):
        value = value.encode("utf-8")

    try:
        group.create_dataset(key, data=value)
    except Exception:
        group.create_dataset(key, data=str(value).encode("utf-8"))


def _cut_movies(
    snirf_path,
    stim_times,
    dyad_id,
    is_child,
    external_structure,
    snirf_goal_structure
):
    """
    Cuts SNIRF into 3 movie files according to stim_times
    and saves using EXTERNAL_STRUCTURE.
    """

    role_key = "child_dir" if is_child else "caregiver_dir"

    # --- resolve base output paths ---
    root = external_structure["root"]["format"](dyad_id)
    dyad = external_structure["root"]["dyad"]["format"](dyad_id)
    modality = external_structure["root"]["dyad"]["modality"]["format"](dyad_id)

    role_struct = external_structure["root"]["dyad"]["modality"][role_key]
    role_dir = role_struct["format"](dyad_id)

    base_path = os.path.join(root, dyad, modality, role_dir)

    os.makedirs(base_path, exist_ok=True)

    with h5py.File(snirf_path, "r") as f:
        snirf_dict = snirf.h5_to_dict(f)

    nirs = snirf_dict.get("nirs", {})

    segments = {
        "1": (stim_times[0], stim_times[1]),
        "3": (stim_times[2], stim_times[3]),
        "5": (stim_times[4], stim_times[5]),
    }

    _check_overlap(segments)

    for stim_key, (t_start, t_end) in segments.items():

        movie_key = conf.MOVIE_MAP[stim_key]
        filename = role_struct[movie_key]["format"](dyad_id)
        output_path = os.path.join(base_path, filename)

        ref_container = nirs.get("data1")

        if ref_container is None or "time" not in ref_container:
            print(f"[WARN] {dyad_id} {movie_key}: missing reference time")
            continue

        ref_time = ref_container["time"]
        _, ref_indices = _adjust_time(ref_time, t_start, t_end)

        if ref_indices is None:
            print(f"[WARN] {dyad_id} {movie_key}: empty segment (reference)")
            continue

        with h5py.File(output_path, "w") as out_f:
            nirs_grp = out_f.create_group("nirs")
            written_any = False

            for container_name, keep in snirf_goal_structure.items():

                if not keep or container_name not in nirs:
                    continue

                container = nirs[container_name]

                # =========================================================
                # META DATA TAGS (special handling)
                # =========================================================
                if container_name == "metaDataTags":

                    grp = nirs_grp.create_group("metaDataTags")

                    adjusted_meta = _adjust_metaDataTags(
                        container,
                        ref_indices,
                        ref_time
                    )

                    if adjusted_meta is None:
                        continue

                    for key, value in container.items():

                        # ----------------------------------------
                        # if adjusted version exists → use it
                        # ----------------------------------------
                        if key in adjusted_meta:
                            _safe_write_dataset(grp, key, adjusted_meta[key])

                        # ----------------------------------------
                        # otherwise copy original unchanged
                        # ----------------------------------------
                        else:
                            _safe_write_dataset(grp, key, value)

                    written_any = True
                    continue

                # =========================================================
                # TIME-BASED CONTAINERS
                # =========================================================
                if isinstance(container, dict) and "time" in container:

                    time = container["time"]

                    if len(time) <= max(ref_indices):
                        print(f"[WARN] {dyad_id} {movie_key} {container_name}: index out of bounds")
                        continue

                    new_time = time[ref_indices]
                    new_time = new_time - new_time[0]

                    grp = nirs_grp.create_group(container_name)

                    for key, value in container.items():

                        # ---- time ----
                        if key == "time":
                            grp.create_dataset("time", data=new_time)

                        # ---- dataTimeSeries ----
                        elif key == "dataTimeSeries":

                            if len(value) != len(time):
                                print(f"[WARN] length mismatch in {container_name}")
                                continue

                            new_data = _adjust_dataTimeSeries(value, ref_indices)
                            grp.create_dataset("dataTimeSeries", data=new_data)

                        # ---- EVERYTHING ELSE (unaltered but safe) ----
                        else:
                            _safe_write_dataset(grp, key, value)

                    written_any = True
                    continue

                # =========================================================
                # NON-TIME CONTAINERS (PURE COPY, SAFE ONLY)
                # =========================================================
                grp = nirs_grp.create_group(container_name)

                if isinstance(container, dict):
                    for key, value in container.items():
                        _safe_write_dataset(grp, key, value)
                else:
                    _safe_write_dataset(grp, "value", container)

                written_any = True

        # =========================================================
        # FINAL CHECK
        # =========================================================
        if not written_any:
            print(f"[WARN] Removing empty file: {output_path}")
            os.remove(output_path)
        else:
            print(f"Saved: {output_path}")



def cut_all_movies(
        paths_children=conf.OUTPUT_PATHS_CHILD,
        paths_caregivers=conf.OUTPUT_PATHS_CAREGIVER,
        stim_times=conf.STIM_TIME_FILE,
        external_structure=conf.EXTERNAL_STRUCTURE,
        snirf_goal_structure=conf.SNIRF_GOAL_STRUCTURE
):

    # -------------------------------------------------
    # load stim times
    # -------------------------------------------------
    stim_df = pd.read_csv(stim_times, sep=None, engine="python")
    stim_df = stim_df.set_index("dyad_id")

    # -------------------------------------------------
    # helper: process one table (children/caregivers)
    # -------------------------------------------------
    def process_table(df_path, is_child):

        df = pd.read_csv(df_path, sep=None, engine="python")

        for _, row in df.iterrows():
            dyad_id = row["dyad_id"]

            # -------------------------------------------------
            # get stim times (unordered -> fix ordering)
            # -------------------------------------------------
            if dyad_id not in stim_df.index:
                print(f"[WARN] missing stim for {dyad_id}")
                continue

            # -------------------------------------------------
            # 1. CUT MOVIES SNIRF
            # -------------------------------------------------
            movie_path = row["movies"]

            if isinstance(movie_path, str) and os.path.exists(movie_path):
                stim_row = stim_df.loc[dyad_id]

                stim_times_list = [
                    stim_row["1"], stim_row["2"],
                    stim_row["3"], stim_row["4"],
                    stim_row["5"], stim_row["6"]
                ]

                # IMPORTANT: convert unordered stim → pairs
                stim_pairs = {
                    "1": (stim_times_list[0], stim_times_list[1]),
                    "3": (stim_times_list[2], stim_times_list[3]),
                    "5": (stim_times_list[4], stim_times_list[5]),
                }

                _cut_movies(
                    snirf_path=movie_path,
                    stim_times=[
                        stim_pairs["1"][0], stim_pairs["1"][1],
                        stim_pairs["3"][0], stim_pairs["3"][1],
                        stim_pairs["5"][0], stim_pairs["5"][1],
                    ],
                    dyad_id=dyad_id,
                    is_child=is_child,
                    external_structure=external_structure,
                    snirf_goal_structure=snirf_goal_structure
                )
            else:
                print(f"[WARN] missing movies for {dyad_id}")

            # -------------------------------------------------
            # 2. COPY FC1 / FC2 WHOLE FILES
            # -------------------------------------------------
            role_key = "child_dir" if is_child else "caregiver_dir"

            role_struct = external_structure["root"]["dyad"]["modality"][role_key]
            base_root = external_structure["root"]["format"](dyad_id)
            dyad_dir = external_structure["root"]["dyad"]["format"](dyad_id)
            modality = external_structure["root"]["dyad"]["modality"]["format"](dyad_id)

            base_path = os.path.join(base_root, dyad_dir, modality, role_struct["format"](dyad_id))

            for fc_key in ["fc1", "fc2"]:

                fc_path = row.get(fc_key, None)

                if not isinstance(fc_path, str) or not os.path.exists(fc_path):
                    continue

                filename = role_struct[fc_key]["format"](dyad_id)
                out_path = os.path.join(base_path, filename)

                os.makedirs(base_path, exist_ok=True)

                shutil.copy2(fc_path, out_path)
                print(f"[FC COPY] {dyad_id} {fc_key} → {out_path}")

    # -------------------------------------------------
    # run both roles
    # -------------------------------------------------
    process_table(paths_children, is_child=True)
    process_table(paths_caregivers, is_child=False)

if __name__ == "__main__":
    create_struct_skeleton(
        comp_merged=conf.COMP_MERGED,
        external_structure=conf.EXTERNAL_STRUCTURE
    )

    cut_all_movies()
