"""
A script to explore the radiation belt pass statistics.
"""

import pathlib

import matplotlib.pyplot as plt
from matplotlib.transforms import Transform
import pandas as pd

from sampex_microburst_indices import config

file_name = 'sampex_passes_v0.csv'
file_path = pathlib.Path(config.PROJECT_DIR, '..', 'data', file_name)

catalog = pd.read_csv(file_path)
catalog = catalog[catalog['max_att_flag'] < 100]
print(catalog[['duration_s']].describe())

pass_threshold_min = 5
n_short_passes = catalog[catalog['duration_s']/60 < pass_threshold_min].shape[0]
n_long_passes = catalog[catalog['duration_s']/60 > pass_threshold_min].shape[0]

print(f'Totals: passes={catalog.shape[0]}, short={n_short_passes}, long={n_long_passes}')
print(f'Percentages: short={100*n_short_passes/catalog.shape[0]}, long={100*n_long_passes/catalog.shape[0]}')

fig, ax = plt.subplots()
ax.hist(catalog['duration_s']/60)
ax.set_title('SAMPEX | Radiation Belt Pass Duration | 4 < L < 8')
ax.set_ylabel('Number of radiation belt passes')
ax.set_xlabel('Duration [minutes]')
ax.set_yscale('log')

s = (
    f'$N_{{< {pass_threshold_min} min}}={{{n_short_passes/100000}}} \\times 10^{{5}}$\n'
    f'$N_{{> {pass_threshold_min} min}}={{{n_long_passes/10000}}} \\times 10^{{4}}$\n'
    f'long/total={round(n_long_passes/catalog.shape[0], 3)}'
     )
ax.text(0.4, 0.9, s, transform=ax.transAxes, ha='left', va='top', fontsize=12)

plt.tight_layout()
plt.show()