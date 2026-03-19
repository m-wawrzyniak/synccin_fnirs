import h5py
import numpy as np
import pandas as pd
import os
import re
from collections import defaultdict

import config_handling as conf


def create_meta_df(
    folder_path,
    output_data_completeness=None,
    output_data_paths=None
):
    """
    Tworzy dwa DataFrame'y:

    1) completeness_df
       1 -> znaleziono .snirf
       2 -> znaleziono plik segmentu, ale nie .snirf
       0 -> brak pliku

    2) paths_df
       zawiera ścieżki do .snirf (tam gdzie completeness == 1)

    Oba mogą zostać zapisane opcjonalnie.
    """

    dyad_pattern = re.compile(r'w[_]?(\d{3})', re.IGNORECASE)
    segments = ['movies', 'fc1', 'fc2']

    completeness = defaultdict(lambda: {seg: 0 for seg in segments})
    paths = defaultdict(lambda: {seg: None for seg in segments})

    for filename in os.listdir(folder_path):
        filepath = os.path.join(folder_path, filename)

        if not os.path.isfile(filepath):
            continue

        dyad_match = dyad_pattern.search(filename)
        if not dyad_match:
            continue

        dyad_number = dyad_match.group(1)
        dyad_id = f"W{dyad_number}"

        lower_name = filename.lower()

        for seg in segments:
            if seg in lower_name:
                ext = os.path.splitext(filename)[1].lower()

                if ext == ".snirf":
                    completeness[dyad_id][seg] = 1
                    paths[dyad_id][seg] = filepath
                else:
                    if completeness[dyad_id][seg] != 1:
                        completeness[dyad_id][seg] = 2

    # ---- completeness DF ----
    completeness_df = pd.DataFrame.from_dict(completeness, orient='index')
    completeness_df.index.name = "dyad_id"
    completeness_df = completeness_df.reset_index()

    # ---- paths DF ----
    paths_df = pd.DataFrame.from_dict(paths, orient='index')
    paths_df.index.name = "dyad_id"
    paths_df = paths_df.reset_index()

    # sortowanie
    for df in [completeness_df, paths_df]:
        df["dyad_num"] = df["dyad_id"].str.extract(r'(\d+)').astype(int)
        df.sort_values("dyad_num", inplace=True)
        df.drop(columns="dyad_num", inplace=True)
        df.reset_index(drop=True, inplace=True)

    # zapis opcjonalny
    if output_data_completeness is not None:
        completeness_df.to_csv(output_data_completeness, index=False)

    if output_data_paths is not None:
        paths_df.to_csv(output_data_paths, index=False)

    return completeness_df, paths_df


def merge_meta(child_df, caregiver_df, output_path=None):
    """
    Łączy dwa DataFrame'y (child + caregiver) po dyad_id.

    Wynikowe kolumny:
    dyad_id,
    movies_child, fc1_child, fc2_child,
    movies_care, fc1_care, fc2_care

    Jeśli output_path podane, zapisuje CSV.
    """

    # kopiujemy żeby nie modyfikować oryginałów
    child_df = child_df.copy()
    caregiver_df = caregiver_df.copy()

    # rename kolumn
    child_df = child_df.rename(columns={
        "movies": "movies_child",
        "fc1": "fc1_child",
        "fc2": "fc2_child"
    })

    caregiver_df = caregiver_df.rename(columns={
        "movies": "movies_care",
        "fc1": "fc1_care",
        "fc2": "fc2_care"
    })

    # merge outer — żeby nie zgubić żadnej diady
    merged_df = pd.merge(
        child_df,
        caregiver_df,
        on="dyad_id",
        how="outer"
    )

    # brakujące wartości ustawiamy na 0
    merged_df = merged_df.fillna(0)

    # konwersja do int (bo fillna robi float)
    for col in merged_df.columns:
        if col != "dyad_id":
            merged_df[col] = merged_df[col].astype(int)

    # sortowanie po numerze diady
    merged_df["dyad_num"] = merged_df["dyad_id"].str.extract(r'(\d+)').astype(int)
    merged_df = (
        merged_df
        .sort_values("dyad_num")
        .drop(columns="dyad_num")
        .reset_index(drop=True)
    )

    # opcjonalny zapis
    if output_path is not None:
        merged_df.to_csv(output_path, index=False)

    return merged_df


def h5_to_dict(obj):
    """
    Recursively extracts data and attributes, handling scalar vs array datasets.
    """
    d = {}

    # 1. Extract Attributes (Metadata)
    for key, val in obj.attrs.items():
        if isinstance(val, bytes):
            val = val.decode('utf-8')
        d[f"ATTR_{key}"] = val

    # 2. Handle Groups (Folders)
    if isinstance(obj, h5py.Group):
        for key, val in obj.items():
            d[key] = h5_to_dict(val)

    # 3. Handle Datasets (The actual data)
    elif isinstance(obj, h5py.Dataset):
        # Check if the dataset is a scalar (fixed the ValueError here)
        if obj.ndim == 0:
            data = obj[()]  # Use empty tuple to read scalar
        else:
            data = obj[:]  # Use slice for arrays

        # Clean up byte strings to normal text
        if isinstance(data, bytes):
            data = data.decode('utf-8')
        elif isinstance(data, np.ndarray) and data.dtype.kind == 'S':
            data = np.char.decode(data, 'utf-8')

        return data

    return d


def extract_movies_stim_info(
        meta_df,
        snirf_dir_child,
        snirf_dir_caregiver,
        output_path=None
):
    """
    Ekstrahuje informacje o stim1–stim6 z segmentu movies
    i buduje DataFrame:

    dyad_id | <stim1_name> | ... | <stim6_name>
    """

    results = []

    for _, row in meta_df.iterrows():
        dyad_id = row["dyad_id"]
        dyad_number = dyad_id[1:]  # np. "095"

        snirf_file_path = None

        # 1️⃣ sprawdź child
        if row.get("movies_child", 0) == 1:
            snirf_file_path = _find_movies_file(
                snirf_dir_child,
                dyad_number
            )

        # 2️⃣ jeśli nie ma child, sprawdź caregiver
        elif row.get("movies_care", 0) == 1:
            snirf_file_path = _find_movies_file(
                snirf_dir_caregiver,
                dyad_number
            )

        if snirf_file_path is None:
            continue

        # 3️⃣ wczytaj snirf (HDF5)
        with h5py.File(snirf_file_path, "r") as f:
            snirf_dict = h5_to_dict(f)

        if "nirs" not in snirf_dict:
            continue

        nirs = snirf_dict["nirs"]

        row_dict = {"dyad_id": dyad_id}

        # 4️⃣ iteracja po stim1–stim6
        for i in range(1, 7):
            stim_key = f"stim{i}"

            if stim_key not in nirs:
                continue

            stim = nirs[stim_key]

            stim_name = stim.get("name", f"stim{i}")
            stim_data = stim.get("data", None)

            if isinstance(stim_data, np.ndarray) and stim_data.size > 0:
                value = stim_data.flatten()[0]
            else:
                value = np.nan

            row_dict[stim_name] = value

        results.append(row_dict)

    # 5️⃣ budowa DataFrame
    result_df = pd.DataFrame(results)

    # sortowanie
    result_df["dyad_num"] = result_df["dyad_id"].str.extract(r'(\d+)').astype(int)
    result_df = (
        result_df
        .sort_values("dyad_num")
        .drop(columns="dyad_num")
        .reset_index(drop=True)
    )

    # zapis
    if output_path is not None:
        result_df.to_csv(output_path, index=False)

    return result_df


def _find_movies_file(folder, dyad_number):
    """
    Znajduje plik movies.snirf dla danej diady.
    """
    pattern = re.compile(rf"w[_]?{dyad_number}", re.IGNORECASE)

    for fname in os.listdir(folder):
        if (
                pattern.search(fname)
                and "movies" in fname.lower()
                and fname.lower().endswith(".snirf")
        ):
            return os.path.join(folder, fname)

    return None


def create_movie_order_df(stim_df, output_path=None):

    results = []

    for _, row in stim_df.iterrows():
        dyad_id = row["dyad_id"]

        # zbieramy tylko 1,3,5
        times = []

        for stim_key in ["1", "3", "5"]:
            if stim_key in row and not pd.isna(row[stim_key]):
                times.append((stim_key, row[stim_key]))

        # sortowanie po czasie
        times_sorted = sorted(times, key=lambda x: x[1])

        ordered_movies = [conf.MOVIE_MAP[t[0]] for t in times_sorted]

        # upewniamy się, że zawsze mamy 3 kolumny
        while len(ordered_movies) < 3:
            ordered_movies.append(np.nan)

        results.append({
            "dyad_id": dyad_id,
            "first_mov": ordered_movies[0],
            "second_mov": ordered_movies[1],
            "third_mov": ordered_movies[2]
        })

    result_df = pd.DataFrame(results)

    # sortowanie po numerze diady
    result_df["dyad_num"] = result_df["dyad_id"].str.extract(r'(\d+)').astype(int)
    result_df = (
        result_df
        .sort_values("dyad_num")
        .drop(columns="dyad_num")
        .reset_index(drop=True)
    )

    if output_path is not None:
        result_df.to_csv(output_path, index=False)

    return result_df


if __name__ == "__main__":
    cgs_df, _ = create_meta_df(
        folder_path=conf.SNIRF_DIR_CAREGIVER,
        output_data_completeness=None,#conf.OUTPUT_COMP_CAREGIVER
        output_data_paths=conf.OUTPUT_PATHS_CAREGIVER
    )

    cls_df, _ = create_meta_df(
        folder_path=conf.SNIRF_DIR_CHILD,
        output_data_completeness=None,#conf.OUTPUT_COMP_CHILD
        output_data_paths=conf.OUTPUT_PATHS_CHILD
    )

    merge_df = merge_meta(
        caregiver_df=cgs_df,
        child_df=cls_df,
        output_path=conf.COMP_MERGED
    )

    stim_time_df = extract_movies_stim_info(
        meta_df=merge_df,
        snirf_dir_child=conf.SNIRF_DIR_CHILD,
        snirf_dir_caregiver=conf.SNIRF_DIR_CAREGIVER,
        output_path=conf.STIM_TIME_FILE
    )

    create_movie_order_df(
        stim_df=stim_time_df,
        output_path=conf.STIM_ORDER_FILE
    )

