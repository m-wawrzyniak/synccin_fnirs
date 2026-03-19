import os
import shutil
import pandas as pd

from mov_time_order import create_meta_df

ROOT = "/media/mateusz-wawrzyniak/ADATA SE880/DATA/FNIRS/fnirs_data_raw/"
# ROOT = "F:\DATA\dane_fnirs\"

SNIRF_DIR_CAREGIVER = f"{ROOT}matka"
SNIRF_DIR_CHILD = f"{ROOT}dziecko"

OUTPUT_PATHS_CAREGIVER =  f"{ROOT}meta_paths_caregiver.csv"
OUTPUT_PATHS_CHILD =  f"{ROOT}meta_paths_child.csv"

OUTPUT_INTERNAL_DB = "/media/mateusz-wawrzyniak/ADATA SE880/DATA/FNIRS/fnirs_data_internal_format/"

def create_internal_db_format(paths_df_child, paths_df_care, output_db_dir):
    """
    Tworzy strukturę folderów:
    Wxxx/
        caregiver/
            cg_mov.snirf, cg_fc1.snirf, cg_fc2.snirf
        child/
            ch_mov.snirf, ch_fc1.snirf, ch_fc2.snirf
    i kopiuje odpowiednie pliki.
    """

    segments = ['movies', 'fc1', 'fc2']

    # upewnij się, że output_dir istnieje
    os.makedirs(output_db_dir, exist_ok=True)

    # iterujemy po wszystkich dyadach (uniquely w child i caregiver)
    dyad_ids = set(paths_df_child["dyad_id"]).union(paths_df_care["dyad_id"])

    for dyad_id in dyad_ids:
        dyad_folder = os.path.join(output_db_dir, dyad_id)
        child_folder = os.path.join(dyad_folder, "child")
        care_folder = os.path.join(dyad_folder, "caregiver")

        os.makedirs(child_folder, exist_ok=True)
        os.makedirs(care_folder, exist_ok=True)

        # --- child ---
        row_child = paths_df_child[paths_df_child["dyad_id"] == dyad_id]
        if not row_child.empty:
            row_child = row_child.iloc[0]
            for seg in segments:
                src_path = row_child.get(seg)
                if pd.notna(src_path):
                    ext = os.path.splitext(src_path)[1]
                    dst_name = f"ch_{seg}{ext}"
                    dst_path = os.path.join(child_folder, dst_name)
                    shutil.copy2(src_path, dst_path)

        # --- caregiver ---
        row_care = paths_df_care[paths_df_care["dyad_id"] == dyad_id]
        if not row_care.empty:
            row_care = row_care.iloc[0]
            for seg in segments:
                src_path = row_care.get(seg)
                if pd.notna(src_path):
                    ext = os.path.splitext(src_path)[1]
                    dst_name = f"cg_{seg}{ext}"
                    dst_path = os.path.join(care_folder, dst_name)
                    shutil.copy2(src_path, dst_path)

    print(f"Struktura snirfów utworzona w: {output_db_dir}")

if __name__ == "__main__":
    _, cgs_df = create_meta_df(
        folder_path=SNIRF_DIR_CAREGIVER,
        output_data_paths=OUTPUT_PATHS_CAREGIVER
    )

    _, cls_df = create_meta_df(
        folder_path=SNIRF_DIR_CHILD,
        output_data_paths=OUTPUT_PATHS_CHILD
    )

    create_internal_db_format(
        paths_df_child=cls_df,
        paths_df_care=cgs_df,
        output_db_dir=OUTPUT_INTERNAL_DB
    )