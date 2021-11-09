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

### All radiation belt passes
fig1, ax = plt.subplots(1, 3, figsize=(10, 5))

ax[0].hist(catalog['AE'], bins=50)
ax[0].set_xlabel('AE')
ax[0].set_ylabel('Number of radiation belt passes')
ax[0].set_yscale('log')

ax[1].hist(catalog['AU'], bins=50)
ax[1].set_xlabel('AU')
ax[1].set_yscale('log')

ax[2].hist(catalog['AL'], bins=50)
ax[2].set_xlabel('AL')
ax[2].set_yscale('log')

fig1.suptitle('SAMPEX-HILT | Microburst occurrence in 4 < L < 8 | All MLT | All Passes')
plt.tight_layout()

### Only radiation belt passes with microbursts
microburst_passes_catalog = catalog[catalog['microburst_count'] > 0]
fig2, bx = plt.subplots(1, 3, figsize=(10, 5))

bx[0].hist(microburst_passes_catalog['AE'], bins=50)
bx[0].set_xlabel('AE')
bx[0].set_ylabel('Number of radiation belt passes')
bx[0].set_yscale('log')

bx[1].hist(microburst_passes_catalog['AU'], bins=50)
bx[1].set_xlabel('AU')
bx[1].set_yscale('log')

bx[2].hist(microburst_passes_catalog['AL'], bins=50)
bx[2].set_xlabel('AL')
bx[2].set_yscale('log')

fig2.suptitle('SAMPEX-HILT | Microburst occurrence in 4 < L < 8 | All MLT | > 1 observed microburst')
plt.tight_layout()

### Only radiation belt passes without microbursts
no_microburst_passes_catalog = catalog[catalog['microburst_count'] == 0]
fig3, cx = plt.subplots(1, 3, figsize=(10, 5))

cx[0].hist(no_microburst_passes_catalog['AE'], bins=50)
cx[0].set_xlabel('AE')
cx[0].set_ylabel('Number of radiation belt passes')
cx[0].set_yscale('log')

cx[1].hist(no_microburst_passes_catalog['AU'], bins=50)
cx[1].set_xlabel('AU')
cx[1].set_yscale('log')

cx[2].hist(no_microburst_passes_catalog['AL'], bins=50)
cx[2].set_xlabel('AL')
cx[2].set_yscale('log')

fig3.suptitle('SAMPEX-HILT | Microburst occurrence in 4 < L < 8 | All MLT | No observed microburst')
plt.tight_layout()

plt.show()