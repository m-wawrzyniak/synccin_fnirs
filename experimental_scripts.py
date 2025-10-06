import pickle
from pprint import pprint

name = "C://Users//Badania//OneDrive//Pulpit//Syncc-In//fnirs_data//psychopy_logs//W_058_et_syncc_in_procedure_2025-09-20_12h24.55.946.psydat"
try:
    with open(name, 'rb') as f:
        dane = pickle.load(f)
    # Tutaj możesz pracować z odzyskanymi danymi
    print("expInfo (extraInfo):")
    pprint(dane.extraInfo)
except FileNotFoundError:
    print("Plik nie został znaleziony.")
except Exception as e:
    print(f"Wystąpił błąd podczas odczytu pliku: {e}")