import pathlib

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

from sampex_microburst_indices import config

file_name = 'sampex_passes_v0.csv'
file_path = pathlib.Path(config.PROJECT_DIR, '..', 'data', file_name)

# Load and filter
catalog = pd.read_csv(file_path)
# Default filters for all passes.
catalog = catalog[catalog['max_att_flag'] < 100]
catalog = catalog[catalog['duration_s'] < 5*60]

microburst_passes_catalog = catalog[catalog['microburst_count'] > 0]
no_microburst_passes_catalog = catalog[catalog['microburst_count'] == 0]

fig, ax = plt.subplots(3, 3, figsize=(10, 10))

# First row: all radiation belt passes
ax[0, 0].scatter(catalog['microburst_prob'], catalog['AE'], color='k')
ax[0, 0].set_xlabel('microburst_prob')
ax[0, 0].set_ylabel('AE')

ax[0, 1].scatter(catalog['microburst_prob'], catalog['AU'], color='k')
ax[0, 1].set_xlabel('microburst_prob')
ax[0, 1].set_ylabel('AU')

ax[0, 2].scatter(catalog['microburst_prob'], catalog['AL'], color='k')
ax[0, 2].set_xlabel('microburst_prob')
ax[0, 2].set_ylabel('AL')

# Second row: radiation belt passes with microbursts
ax[1, 0].scatter(microburst_passes_catalog['microburst_prob'], microburst_passes_catalog['AE'], color='k')
ax[1, 0].set_xlabel('microburst_prob')
ax[1, 0].set_ylabel('AE')

ax[1, 1].scatter(microburst_passes_catalog['microburst_prob'], microburst_passes_catalog['AU'], color='k')
ax[1, 1].set_xlabel('microburst_prob')
ax[1, 1].set_ylabel('AU')

ax[1, 2].scatter(microburst_passes_catalog['microburst_prob'], microburst_passes_catalog['AL'], color='k')
ax[1, 2].set_xlabel('microburst_prob')
ax[1, 2].set_ylabel('AL')

# Third row: no microbursts
ax[2, 0].scatter(no_microburst_passes_catalog['microburst_prob'], no_microburst_passes_catalog['AE'], color='k')
ax[2, 0].set_xlabel('microburst_prob')
ax[2, 0].set_ylabel('AE')

ax[2, 1].scatter(no_microburst_passes_catalog['microburst_prob'], no_microburst_passes_catalog['AU'], color='k')
ax[2, 1].set_xlabel('microburst_prob')
ax[2, 1].set_ylabel('AU')

ax[2, 2].scatter(no_microburst_passes_catalog['microburst_prob'], no_microburst_passes_catalog['AL'], color='k')
ax[2, 2].set_xlabel('microburst_prob')
ax[2, 2].set_ylabel('AL')

fig.suptitle('SAMPEX-HILT | AE vs. microburst occurrence | 4 < L < 8 | All MLT')
plt.tight_layout()

plt.show()