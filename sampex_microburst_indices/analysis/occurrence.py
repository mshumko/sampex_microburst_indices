import pathlib

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

from sampex_microburst_indices import config

file_name = 'sampex_passes_v0.csv'
file_path = pathlib.Path(config.PROJECT_DIR, '..', 'data', file_name)

### All good passes
catalog = pd.read_csv(file_path)
catalog = catalog[catalog['max_att_flag'] < 100]
catalog = catalog[catalog['duration_s'] < 5*60]
# print(catalog.describe())

fig1, ax = plt.subplots(1, 2, figsize=(10, 5))

ax[0].hist(catalog['microburst_count'], bins=np.linspace(0, 200))
ax[0].set_xlabel('microbursts/pass')
ax[0].set_xlim(0, 200)
ax[0].set_yscale('log')

ax[1].hist(catalog['microburst_count']/catalog['duration_s'], bins=np.linspace(0, 1))
ax[1].set_xlabel('microbursts/second')
ax[1].set_xlim(0, 1)
ax[1].set_yscale('log')

fig1.suptitle('SAMPEX-HILT | Microburst occurrence in 4 < L < 8 | All MLT')
plt.tight_layout()

### Morning MLT
morning_catalog = catalog.copy()
morning_catalog = morning_catalog[(morning_catalog['mean_MLT'] > 0) &
                                  (morning_catalog['mean_MLT'] < 12)]

fig2, bx = plt.subplots(1, 2, figsize=(10, 5))

bx[0].hist(morning_catalog['microburst_count'], bins=np.linspace(0, 200))
bx[0].set_xlabel('microbursts/pass')
bx[0].set_xlim(0, 200)
bx[0].set_yscale('log')

bx[1].hist(morning_catalog['microburst_count']/morning_catalog['duration_s'], bins=np.linspace(0, 1))
bx[1].set_xlabel('microbursts/second')
bx[1].set_xlim(0, 1)
bx[1].set_yscale('log')

fig2.suptitle('SAMPEX-HILT | Microburst occurrence in 4 < L < 8 | 0 < MLT < 12')
plt.tight_layout()

### Afternoon MLT
afternoon_catalog = catalog.copy()
afternoon_catalog = afternoon_catalog[(afternoon_catalog['mean_MLT'] > 12) &
                                      (afternoon_catalog['mean_MLT'] < 24)]

fig3, cx = plt.subplots(1, 2, figsize=(10, 5))

cx[0].hist(afternoon_catalog['microburst_count'], bins=np.linspace(0, 200))
cx[0].set_xlabel('microbursts/pass')
cx[0].set_xlim(0, 200)
cx[0].set_yscale('log')

cx[1].hist(afternoon_catalog['microburst_count']/afternoon_catalog['duration_s'], bins=np.linspace(0, 1))
cx[1].set_xlabel('microbursts/second')
cx[1].set_xlim(0, 1)
cx[1].set_yscale('log')

fig3.suptitle('SAMPEX-HILT | Microburst occurrence in 4 < L < 8 | 12 < MLT < 24')
plt.tight_layout()

plt.show()