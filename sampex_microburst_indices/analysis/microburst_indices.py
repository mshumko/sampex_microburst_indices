# Visualize the distribution of the number of microbursts vs 
# all of the indices.

import pandas as pd
import matplotlib.pyplot as plt

from sampex_microburst_indices.load.catalog import Catalog

columns = ['AE', 'AU', 'AL', 'SYM/D', 'SYM/H', 'ASY/D', 'ASY/H']
catalog = Catalog(0).load()

fig, ax = plt.subplots(1, len(columns), figsize=(12, 3))

for column, ax_i in zip(columns, ax):
    ax_i.hist(catalog.loc[:, column], bins=20)
    ax_i.set_xlabel(column)

plt.tight_layout()
plt.show()