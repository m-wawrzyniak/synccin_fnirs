import os
import pandas as pd
import h5py
import numpy as np
import shutil

import snirf_handling as snirf
import config_handling as conf

def _resolve_path(dyad_id, external_structure, role=None, file_key=None):
    """
    Resolves paths from EXTERNAL_STRUCTURE.

    Returns:
        dict with:
            root
            modality
            dyad
            role (optional)
            full_dir (deepest directory)
            file_path (optional)
    """

    root_struct = external_structure["root"]
    modality_struct = root_struct["modality"]
    dyad_struct = modality_struct["dyad"]

    # -------------------------
    # BASE PATHS
    # -------------------------
    root_path = root_struct["format"](dyad_id)

    modality_path = os.path.join(
        root_path,
        modality_struct["format"](dyad_id)
    )

    dyad_path = os.path.join(
        modality_path,
        dyad_struct["format"](dyad_id)
    )

    result = {
        "root": root_path,
        "modality": modality_path,
        "dyad": dyad_path
    }

    # -------------------------
    # ROLE (child / caregiver)
    # -------------------------
    if role is not None:

        role_key = f"{role}_dir"
        role_struct = dyad_struct[role_key]

        role_path = os.path.join(
            dyad_path,
            role_struct["format"](dyad_id)
        )

        result["role"] = role_path
        result["full_dir"] = role_path

        # -------------------------
        # FILE
        # -------------------------
        if file_key is not None:

            if file_key not in role_struct:
                raise ValueError(f"{file_key} not found in {role_key}")

            filename = role_struct[file_key]["format"](dyad_id)

            result["file_path"] = os.path.join(role_path, filename)

    else:
        result["full_dir"] = dyad_path

    return result


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

    for dyad_id in comp_merged["dyad_id"].unique():
        paths = _resolve_path(
            dyad_id,
            external_structure,
            role="child"
        )
        os.makedirs(paths["full_dir"], exist_ok=True)

        paths = _resolve_path(
            dyad_id,
            external_structure,
            role="caregiver"
        )
        os.makedirs(paths["full_dir"], exist_ok=True)

    print("Structure skeleton created successfully.")


def inspect_padding_availability(
    paths_children,
    paths_caregivers,
    stim_times_path
):
    """
    Computes how much data exists:
    - before FIRST presented movie
    - after LAST presented movie

    (respects randomized order of movies)
    """

    stim_df = pd.read_csv(stim_times_path, sep=None, engine="python")
    stim_df = stim_df.set_index("dyad_id")

    def process(df_path, role_name):

        df = pd.read_csv(df_path, sep=None, engine="python")

        print(f"\n===== {role_name.upper()} =====")

        for _, row in df.iterrows():
            dyad_id = row["dyad_id"]

            if dyad_id not in stim_df.index:
                print(f"[WARN] missing stim for {dyad_id}")
                continue

            snirf_path = row.get("movies", None)

            if not isinstance(snirf_path, str) or not os.path.exists(snirf_path):
                print(f"[WARN] missing SNIRF for {dyad_id}")
                continue

            # -------------------------
            # LOAD TIME
            # -------------------------
            with h5py.File(snirf_path, "r") as f:
                snirf_dict = snirf.h5_to_dict(f)

            nirs = snirf_dict.get("nirs", {})
            data1 = nirs.get("data1", {})

            if "time" not in data1:
                print(f"[WARN] no time in {dyad_id}")
                continue

            time = data1["time"]
            t_min = np.min(time)
            t_max = np.max(time)

            # -------------------------
            # STIM SEGMENTS (UNORDERED)
            # -------------------------
            stim_row = stim_df.loc[dyad_id]

            segments = [
                (stim_row["1"], stim_row["2"], "seg1"),
                (stim_row["3"], stim_row["4"], "seg2"),
                (stim_row["5"], stim_row["6"], "seg3"),
            ]

            # -------------------------
            # SORT BY ACTUAL TIME
            # -------------------------
            segments_sorted = sorted(segments, key=lambda x: x[0])

            first_start = segments_sorted[0][0]
            last_end = segments_sorted[-1][1]

            # -------------------------
            # COMPUTE BUFFERS
            # -------------------------
            before = first_start - t_min
            after = t_max - last_end

            print(
                f"{dyad_id} | "
                f"before: {before:.2f}s | "
                f"after: {after:.2f}s"
            )

    process(paths_children, "child")
    process(paths_caregivers, "caregiver")


def _adjust_time(time_array, t_start, t_end, padding=0.0):
    """
    Returns:
    - adjusted time (rebased so that t_start → 0)
    - indices to keep
    """

    t_min = t_start - padding
    t_max = t_end + padding

    mask = (time_array >= t_min) & (time_array <= t_max)

    if not np.any(mask):
        return None, None

    indices = np.where(mask)[0]

    new_time = time_array[indices]
    new_time = new_time - t_start

    return new_time, indices


def _adjust_dataTimeSeries(data, indices):
    """
    Uses indices from _adjust_time
    """
    if indices is None:
        return None

    return data[indices]


def _adjust_metaDataTags(meta, indices, t_start):
    """
    Adjusts metadata according to selected indices and time rebasing.
    """

    adjusted = {}

    # -------------------------
    # missing_sample
    # -------------------------
    if "missing_sample" in meta:
        adjusted["missing_sample"] = meta["missing_sample"][indices]

    # -------------------------
    # sample_index (relative to hardware → just slice)
    # -------------------------
    if "sample_index" in meta:
        adjusted["sample_index"] = meta["sample_index"][indices]

    # -------------------------
    # device_timestamp (NO OFFSET, only slice)
    # -------------------------
    if "device_timestamp" in meta:
        adjusted["device_timestamp"] = meta["device_timestamp"][indices]

    # -------------------------
    # first_timestamp (OFFSET LIKE TIME)
    # -------------------------
    if "first_timestamp" in meta:
        adjusted["first_timestamp"] = meta["first_timestamp"] - t_start

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

    paths = _resolve_path(
        dyad_id,
        external_structure,
        role="child" if is_child else "caregiver"
    )

    base_path = paths["full_dir"]
    os.makedirs(base_path, exist_ok=True)

    # =========================================================
    # LOAD SNIRF
    # =========================================================
    with h5py.File(snirf_path, "r") as f:
        snirf_dict = snirf.h5_to_dict(f)

    nirs = snirf_dict.get("nirs", {})

    # =========================================================
    # STIM SEGMENTS
    # =========================================================
    segments = {
        "1": (stim_times[0], stim_times[1]),
        "3": (stim_times[2], stim_times[3]),
        "5": (stim_times[4], stim_times[5]),
    }

    _check_overlap(segments)

    # =========================================================
    # PROCESS EACH MOVIE
    # =========================================================
    for stim_key, (t_start, t_end) in segments.items():

        movie_key = conf.MOVIE_MAP[stim_key]
        paths = _resolve_path(
            dyad_id,
            external_structure,
            role="child" if is_child else "caregiver",
            file_key=movie_key
        )
        output_path = paths["file_path"]

        # -----------------------------------------------------
        # REFERENCE TIME (GLOBAL INDICES)
        # -----------------------------------------------------
        ref_container = nirs.get("data1")

        if ref_container is None or "time" not in ref_container:
            print(f"[WARN] {dyad_id} {movie_key}: missing reference time")
            continue

        ref_time = ref_container["time"]

        _, ref_indices = _adjust_time(
            ref_time,
            t_start,
            t_end,
            padding=conf.PADDING
        )

        if ref_indices is None:
            print(f"[WARN] {dyad_id} {movie_key}: empty segment")
            continue


        # =====================================================
        # WRITE OUTPUT SNIRF
        # =====================================================
        with h5py.File(output_path, "w") as out_f:

            nirs_grp = out_f.create_group("nirs")
            written_any = False

            for container_name, keep in snirf_goal_structure.items():

                if not keep or container_name not in nirs:
                    continue

                container = nirs[container_name]

                # =================================================
                # META DATA TAGS
                # =================================================
                if container_name == "metaDataTags":

                    grp = nirs_grp.create_group("metaDataTags")

                    adjusted_meta = _adjust_metaDataTags(
                        container,
                        ref_indices,
                        t_start
                    )

                    if adjusted_meta is None:
                        continue

                    for key, value in container.items():

                        if key in adjusted_meta:
                            _safe_write_dataset(grp, key, adjusted_meta[key])
                        else:
                            _safe_write_dataset(grp, key, value)

                    written_any = True
                    continue

                # =================================================
                # TIME-BASED CONTAINERS
                # =================================================
                if isinstance(container, dict) and "time" in container:

                    time = container["time"]

                    if len(time) <= max(ref_indices):
                        print(f"[WARN] {dyad_id} {movie_key} {container_name}: index out of bounds")
                        continue

                    # 🔥 CRITICAL: align to stimulus onset
                    new_time = time[ref_indices] - t_start

                    grp = nirs_grp.create_group(container_name)

                    for key, value in container.items():

                        # ---- TIME ----
                        if key == "time":
                            grp.create_dataset("time", data=new_time)

                        # ---- SIGNAL ----
                        elif key == "dataTimeSeries":

                            if len(value) != len(time):
                                print(f"[WARN] length mismatch in {container_name}")
                                continue

                            new_data = _adjust_dataTimeSeries(value, ref_indices)
                            grp.create_dataset("dataTimeSeries", data=new_data)

                        # ---- EVERYTHING ELSE ----
                        else:
                            _safe_write_dataset(grp, key, value)

                    written_any = True
                    continue

                # =================================================
                # NON-TIME CONTAINERS (PURE COPY)
                # =================================================
                grp = nirs_grp.create_group(container_name)

                if isinstance(container, dict):
                    for key, value in container.items():
                        _safe_write_dataset(grp, key, value)
                else:
                    _safe_write_dataset(grp, "value", container)

                written_any = True


        # =====================================================
        # FINAL CHECK
        # =====================================================
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
            paths = _resolve_path(
                dyad_id,
                external_structure,
                role="child" if is_child else "caregiver"
            )
            base_path = paths["full_dir"]

            for fc_key in ["fc1", "fc2"]:

                fc_path = row.get(fc_key, None)

                if not isinstance(fc_path, str) or not os.path.exists(fc_path):
                    continue

                paths = _resolve_path(
                    dyad_id,
                    external_structure,
                    role="child" if is_child else "caregiver",
                    file_key=fc_key
                )

                out_path = paths["file_path"]

                os.makedirs(base_path, exist_ok=True)

                shutil.copy2(fc_path, out_path)
                print(f"[FC COPY] {dyad_id} {fc_key} → {out_path}")

    # -------------------------------------------------
    # run both roles
    # -------------------------------------------------
    process_table(paths_children, is_child=True)
    process_table(paths_caregivers, is_child=False)

if __name__ == "__main__":
    """
    inspect_padding_availability(
        paths_children=conf.OUTPUT_PATHS_CHILD,
        paths_caregivers=conf.OUTPUT_PATHS_CAREGIVER,
        stim_times_path=conf.STIM_TIME_FILE
    )
    """
    create_struct_skeleton(
        comp_merged=conf.COMP_MERGED,
        external_structure=conf.EXTERNAL_STRUCTURE
    )

    cut_all_movies()