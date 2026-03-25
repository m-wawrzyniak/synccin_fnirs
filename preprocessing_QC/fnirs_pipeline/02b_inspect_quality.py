import os
import pandas as pd
import seaborn as sns

import matplotlib.pyplot as plt
from local_config import datadir

#%%
dataset = 'KP'

signal_quality_datafile = os.path.join(datadir, dataset, 'summary_fnirs_quality.csv')

data = pd.read_csv(signal_quality_datafile, index_col=0)

#%% CNR
fig, axes = plt.subplots(7, 7, sharex=True)

axes = axes.ravel()

for i_ch in range(49):
    data_ch = data.query('channel == @i_ch')

    data_adult = data_ch.query('member == "adult"')
    data_child = data_ch.query('member == "child"')
    
    plt.sca(axes[i_ch])
    plt.hist(data_adult['cnr'].values)
    plt.hist(data_child['cnr'].values)
    
plt.legend(['adult', 'child'])
plt.suptitle('CNR')

#%% SCI_C
fig, axes = plt.subplots(7, 7, sharex=True)

axes = axes.ravel()

for i_ch in range(49):
    data_ch = data.query('channel == @i_ch')

    data_adult = data_ch.query('member == "adult"')
    data_child = data_ch.query('member == "child"')
    
    plt.sca(axes[i_ch])
    plt.hist(data_adult['sci_c'].values)
    plt.hist(data_child['sci_c'].values)
    
plt.legend(['adult', 'child'])
plt.suptitle('SCI_C')

#%% SCI_P
fig, axes = plt.subplots(7, 7, sharex=True)

axes = axes.ravel()

for i_ch in range(49):
    data_ch = data.query('channel == @i_ch')

    data_adult = data_ch.query('member == "adult"')
    data_child = data_ch.query('member == "child"')
    
    plt.sca(axes[i_ch])
    plt.hist(data_adult['sci_p'].values)
    plt.hist(data_child['sci_p'].values)
    
plt.legend(['adult', 'child'])
plt.suptitle('SCI_P')