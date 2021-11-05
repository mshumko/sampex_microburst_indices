import pathlib

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

from sampex_microburst_indices import config

file_name = 'microburst_catalog.csv'
file_path = pathlib.Path(config.PROJECT_DIR, '..', 'data', file_name)

catalog = pd.read_csv(file_path)
catalog = catalog[catalog['adj_r2'] > 0.5]
print(np.abs(catalog[['fwhm']]).describe())

print(f'Total number of microbursts: {catalog.shape[0]}')
print(f'Number of wide microbursts: {catalog[np.abs(catalog["fwhm"]) > 1].shape[0]}')

plt.hist(np.abs(catalog[['fwhm']]), bins=np.linspace(0, 1))
plt.xlabel('fwhm [s]')
plt.show()