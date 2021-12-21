# Calculate the percen

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from sampex_microburst_indices.load.catalog import Catalog

columns = ['AE', 'AU', 'AL', 'SYM/D', 'SYM/H', 'ASY/D', 'ASY/H']
quantiles = np.linspace(0, 1, 6)
catalog = Catalog(0).load()

q = catalog.loc[:, columns].quantile(q=quantiles)
print(q)