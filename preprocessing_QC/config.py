from pyphysio.loaders import SDto1darray

# experimental settings
members = ['caregiver', 'child']
sessions = ['Talk1', 'Talk2', 'Brave', 'Peppa', 'Incredibles'] #'Secore' not included

margin = 5

#used by imports
def segment_and_save(nirs, t_start, t_stop, outfile, 
                     t_margin = None, fresamp = 10):
    if t_margin is None:
        t_margin = margin
    
    nirs_event = nirs.p.segment_time(t_start-t_margin, t_stop+t_margin)
    nirs_event = nirs_event.p.resample(fresamp)
    
    nirs_event = nirs_event.p.reset_times(-t_margin)
    SDto1darray(nirs_event).to_netcdf(outfile)


marker_map_kp = {
'Brave_start': 'A',   # Start of Video 1 (Brave/Merida) 
'Brave_stop': 'B',    # End of Video 1
'Peppa_start': 'C',   # Start of Video 2 (Peppa Pig) 
'Peppa_stop': 'D',    # End of Video 2
'Incredibles_start': 'E',   # Start of Video 3 (Incredibles) 
'Incredibles_stop': 'F',    # End of Video 3
'Talk1_start': 'G',  # Start of Conversation 1
'Talk1_stop': 'H',   # End of Conversation 1
'Talk2_start': 'I',  # Start of Conversation 2
'Talk2_stop': 'J',   # End of Conversation 2
}

marker_map_ww = {
'Brave_start': 1,   # Start of Video 1 (Brave/Merida) 
'Brave_stop': 2,    # End of Video 1
'Peppa_start': 3,   # Start of Video 2 (Peppa Pig) 
'Peppa_stop': 4,    # End of Video 2
'Incredibles_start': 5,   # Start of Video 3 (Incredibles) 
'Incredibles_stop': 6,    # End of Video 3
'Talk1_start': 7,  # Start of Conversation 1
'Talk1_stop': 8,   # End of Conversation 1
'Talk2_start': 9,  # Start of Conversation 2
'Talk2_stop': 10,   # End of Conversation 2
}

