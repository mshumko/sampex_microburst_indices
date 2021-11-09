"""
A script to explore the radiation belt pass statistics.
"""

import pathlib

import matplotlib.pyplot as plt
import pandas as pd

from sampex_microburst_indices import config

file_name = 'sampex_passes_v0.csv'
file_path = pathlib.Path(config.PROJECT_DIR, '..', 'data', file_name)

catalog = pd.read_csv(file_path)
catalog = catalog[catalog['max_att_flag'] < 100]
print(catalog[['duration_s']].describe())

fig, ax = plt.subplots()
ax.hist(catalog['duration_s']/60)
ax.set_title('SAMPEX | Radiation Belt Pass Duration | 4 < L < 8')
ax.set_xlabel('pass duration')
ax.set_yscale('log')

plt.tight_layout()
plt.show()