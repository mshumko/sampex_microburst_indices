import pathlib

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

from sampex_microburst_indices import config

file_name = 'sampex_passes_v0.csv'
file_path = pathlib.Path(config.PROJECT_DIR, '..', 'data', file_name)

catalog = pd.read_csv(file_path)
print(catalog.describe())

plt.hist(catalog['microburst_count']/catalog['duration_s'], bins=np.linspace(0, 1))
plt.xlabel('microbursts/second')
plt.ylim(0, 4000)
plt.xlim(0, 1)
plt.show()