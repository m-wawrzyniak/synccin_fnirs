#%%
import pyphysio as ph
from pyphysio.loaders import load_snirf
import os
import pandas as pd
from local_config import datadir, importeddir
from config import marker_map_ww, segment_and_save

video_names = {'1': 'Brave', '3': 'Peppa', '5': 'Incredibles'}
#%%
dataset = 'W'
modality = 'FNIRS'

#%%
summary = []
dyads = os.listdir(os.path.join(datadir, dataset))
for dyad in dyads:
    dyad_id = dyad[1:]
    for member in ['mother', 'child']:
        member_code = 'cg' if member == 'mother' else 'ch'
        member_folder = 'caregiver' if member == 'mother' else 'child'
        for session in ['fc1', 'fc2', 'movies']:
            datafile = os.path.join(datadir, dataset, dyad, member, f'{session}.snirf' )
            nirs, stim = load_snirf(datafile, has_stim=True)
            t_events = stim.p.get_times()

            outdir = os.path.join(importeddir, dataset, modality, f'{dataset}_{dyad_id}', member_folder)
            os.makedirs(outdir, exist_ok=True)
                
            if session in ['fc1', 'fc2']:
                t_start = t_events[0]
                t_stop = t_events[1]
                
                session_name = 'Talk1' if session == 'fc1' else 'Talk2'
                outfile_name = f'{dataset}_{dyad_id}_{modality}_{member_code}_{session_name}.nc'
                    
                outfile = os.path.join(outdir, outfile_name)
                
                segment_and_save(nirs, t_start, t_stop, outfile)
                summary.append({'dataset': dataset,
                                'dyad': dyad,
                                'member': member,
                                'session': session_name,
                                't_start': t_start,
                                't_stop': t_stop})
            
            else:
                ev_reverse = {v: k for k, v in stim.attrs['event_codes'].items()}
                t_start_ = t_events[[0, 2, 4]]
                t_stop_ = t_events[[1, 3, 5]]
                event_names = [ev_reverse[k] for k in stim.values[[0, 2, 4]]]

                for i, (t_start, t_stop, event_name) in enumerate(zip(t_start_, t_stop_, event_names)):
                    video_name = video_names[event_name]
                    outfile_name = f'{dataset}_{dyad_id}_{modality}_{member_code}_{video_name}.nc'
                    outfile = os.path.join(outdir, outfile_name)

                    segment_and_save(nirs, t_start, t_stop, outfile)
                    summary.append({'dataset': dataset,
                                    'dyad': dyad,
                                    'member': member,
                                    'session': video_name,
                                    't_start': t_start,
                                    't_stop': t_stop})

#%%                    
summary = pd.DataFrame(summary)
print(summary)