import pathlib

import matplotlib.pyplot as plt
import pandas as pd

from sampex_microburst_indices import config

file_name = 'sampex_passes_v0.csv'
file_path = pathlib.Path(config.PROJECT_DIR, '..', 'data', file_name)

catalog = pd.read_csv(file_path)
print(catalog.describe())