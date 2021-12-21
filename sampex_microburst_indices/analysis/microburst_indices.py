# Visualize the distribution of the number of microbursts vs 
# all of the indices.

import pandas as pd
import matplotlib.pyplot as plt

from sampex_microburst_indices.load.catalog import Catalog

columns = ['AE', 'AU', 'AL']
catalog = Catalog(0).load()
pd.plotting.scatter_matrix(catalog.loc[:, columns], alpha=0.2)
plt.show()

pass