import pathlib

import matplotlib.pyplot as plt
import matplotlib.colors
import pandas as pd
import numpy as np

from sampex_microburst_indices import config

type = 'hist'
file_name = 'sampex_passes_v0.csv'
file_path = pathlib.Path(config.PROJECT_DIR, '..', 'data', file_name)

# Load and filter
catalog = pd.read_csv(file_path)
# Default filters for all passes.
catalog = catalog[catalog['max_att_flag'] < 100]
catalog = catalog[catalog['duration_s'] < 5*60]

fig2, bx = plt.subplots(2, 4, figsize=(10, 5))

if type == 'scatter':
    bx[0, 0].scatter(catalog['microburst_prob'], catalog['SYM/D'], color='k', s=10)
else:
    bx[0, 0].hist2d(catalog['microburst_prob'], catalog['SYM/D'], norm=matplotlib.colors.LogNorm())
bx[0, 0].set_xlabel('microbursts/second')
bx[0, 0].set_ylabel('SYM/D')

if type == 'scatter':
    bx[0, 1].scatter(catalog['microburst_prob'], catalog['SYM/H'], color='k', s=10)
else:
    bx[0, 1].hist2d(catalog['microburst_prob'], catalog['SYM/H'], norm=matplotlib.colors.LogNorm())
bx[0, 1].set_xlabel('microbursts/second')
bx[0, 1].set_ylabel('SYM/H')

if type == 'scatter':
    bx[0, 2].scatter(catalog['microburst_prob'], catalog['ASY/D'], color='k', s=10)
else:
    bx[0, 2].hist2d(catalog['microburst_prob'], catalog['ASY/D'], norm=matplotlib.colors.LogNorm())
bx[0, 2].set_xlabel('microbursts/second')
bx[0, 2].set_ylabel('ASY/D')

if type == 'scatter':
    bx[0, 3].scatter(catalog['microburst_prob'], catalog['ASY/H'], color='k', s=10)
else:
    bx[0, 3].hist2d(catalog['microburst_prob'], catalog['ASY/H'], norm=matplotlib.colors.LogNorm())
bx[0, 3].set_xlabel('microbursts/second')
bx[0, 3].set_ylabel('ASY/H')

if type == 'scatter':
    bx[1, 0].scatter(catalog['microburst_prob'], catalog['AE'], color='k', s=10)
else:
    bx[1, 0].hist2d(catalog['microburst_prob'], catalog['AE'], norm=matplotlib.colors.LogNorm())
bx[1, 0].set_xlabel('microbursts/second')
bx[1, 0].set_ylabel('AE')

if type == 'scatter':
    bx[1, 1].scatter(catalog['microburst_prob'], catalog['AU'], color='k', s=10)
else:
    bx[1, 1].hist2d(catalog['microburst_prob'], catalog['AU'], norm=matplotlib.colors.LogNorm())
bx[1, 1].set_xlabel('microbursts/second')
bx[1, 1].set_ylabel('AU')

if type == 'scatter':
    bx[1, 2].scatter(catalog['microburst_prob'], catalog['AL'], color='k', s=10)
else:
    bx[1, 2].hist2d(catalog['microburst_prob'], catalog['AL'], norm=matplotlib.colors.LogNorm())
bx[1, 2].set_xlabel('microbursts/second')
bx[1, 2].set_ylabel('AL')

bx[1, 3].axis('off')

fig2.suptitle('SAMPEX-HILT | Indices vs. microburst occurrence | 4 < L < 8 | All MLT')
plt.tight_layout()

plt.show()