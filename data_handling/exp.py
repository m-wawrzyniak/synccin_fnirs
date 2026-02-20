import os
import re
from collections import defaultdict
import h5py
import numpy as np
import pandas as pd

def create_meta_df(folder_path, output_path=None):
    """
    Tworzy DataFrame z informacją o dostępności segmentów:
    movies, fc1, fc2

    1 -> znaleziono .snirf
    2 -> znaleziono plik segmentu, ale nie .snirf
    0 -> brak pliku

    Jeśli output_path podane, zapisuje CSV.
    """

    dyad_pattern = re.compile(r'w[_]?(\d{3})', re.IGNORECASE)
    segments = ['movies', 'fc1', 'fc2']

    data = defaultdict(lambda: {seg: 0 for seg in segments})

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
                    data[dyad_id][seg] = 1
                else:
                    if data[dyad_id][seg] != 1:
                        data[dyad_id][seg] = 2

    # konwersja do DataFrame
    df = pd.DataFrame.from_dict(data, orient='index')
    df.index.name = "dyad_id"
    df = df.reset_index()

    # sortowanie po numerze diady
    df["dyad_num"] = df["dyad_id"].str.extract(r'(\d+)').astype(int)
    df = df.sort_values("dyad_num").drop(columns="dyad_num").reset_index(drop=True)

    # opcjonalny zapis
    if output_path is not None:
        df.to_csv(output_path, index=False)

    return df


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

        ordered_movies = [MOVIE_MAP[t[0]] for t in times_sorted]

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


SNIRF_DIR_CAREGIVER = "F:\DATA\dane_fnirs\matka"
OUTPUT_FILE_CAREGIVER = "F:\DATA\dane_fnirs\meta_caregiver.csv"

SNIRF_DIR_CHILD = "F:\DATA\dane_fnirs\dziecko"
OUTPUT_FILE_CHILD = "F:\DATA\dane_fnirs\meta_child.csv"

META_FILE = "F:\DATA\dane_fnirs\meta.csv"
STIM_TIME_FILE = "F:\DATA\dane_fnirs\stim_time_meta.csv"

MOVIE_MAP = {
    "1": "Brave",
    "3": "Peppa Pig",
    "5": "The Incredibles"
}

STIM_ORDER_FILE = "F:\DATA\dane_fnirs\stim_order_meta.csv"

if __name__ == "__main__":
    cgs_df = create_meta_df(
        folder_path=SNIRF_DIR_CAREGIVER,
        output_path=None#OUTPUT_FILE_CAREGIVER
    )

    cls_df = create_meta_df(
        folder_path=SNIRF_DIR_CHILD,
        output_path=None#OUTPUT_FILE_CHILD
    )

    merge_df = merge_meta(
        caregiver_df=cgs_df,
        child_df=cls_df,
        output_path=META_FILE
    )

    stim_time_df = extract_movies_stim_info(
        meta_df=merge_df,
        snirf_dir_child=SNIRF_DIR_CHILD,
        snirf_dir_caregiver=SNIRF_DIR_CAREGIVER,
        output_path=STIM_TIME_FILE
    )

    create_movie_order_df(
        stim_df=stim_time_df,
        output_path=STIM_ORDER_FILE
    )

