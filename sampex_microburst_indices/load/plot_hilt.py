# This program loads the HILT data and parses it into a nice format
from datetime import datetime

# import pandas as pd
# import numpy as np
import matplotlib.pyplot as plt

# from sampex_microburst_indices import config
import sampex_microburst_indices.load.sampex as sampex

day = datetime(2005, 7, 1)

h = sampex.Load_HILT(day)
h.resolve_counts_state4()
# a = Load_Attitude(day)

fig, ax = plt.subplots()
ax.step(h.hilt_resolved.index, h.hilt_resolved.counts, label='HILT', where='post')

ax.set(ylabel='HILT')
# ax.set(ylabel='PET')
# ax.set(ylabel='LICA/Stop')
ax.set_xlabel('Time')

plt.suptitle(f'SAMPEX | {day.date()}')
plt.show()