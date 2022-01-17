import pathlib

import pandas as pd
import numpy as np

from sampex_microburst_indices import config

class Catalog:
    def __init__(self, catalog_version, remove_spin_times=True, parse_dates=False):
        """
        A standardized loader for the microburst catalog.
        """
        self.catalog_version = str(catalog_version)
        self.remove_spin_times = remove_spin_times
        self.parse_dates = parse_dates
        return

    def load(self):
        """
        Loads the microburst catalog into a pd.DataFrame. Optionally filter
        out spin times and parse time stamps (not all cases need time stamp objects).
        """
        file_path = pathlib.Path(config.PROJECT_DIR, '..', 'data', 
            f'microburst_catalog_{self.catalog_version.zfill(2)}.csv')

        self.catalog = pd.read_csv(file_path, index_col=0, parse_dates=self.parse_dates)

        self.catalog.dropna(inplace=True)  # Drop rows with missing attitude data.

        if self.remove_spin_times:
            # See the docs to learn why Att_Flag = 0 or 1
            # http://www.srl.caltech.edu/sampex/DataCenter/docs/att_flag_details.txt
            self.catalog = self.catalog[
                (self.catalog.loc[:, 'Att_Flag'] == 0) |
                (self.catalog.loc[:, 'Att_Flag'] == 1)
            ]
        return self.catalog

    def hist(self, norm_version=None, marginalize_variables=[]):
        """
        Histogram the self.catalog and optionally normalize it by a 
        normalization file (that is optionally margianalized if 
        marginalize_variables are specified).
        """

        if norm_version is not None:
            self.load_norm(norm_version, marginalize_variables=marginalize_variables)
        return

    def load_norm(self, norm_version, marginalize_variables=[]):
        """
        Load the normalization .npz file with the norm_version number and
        optionally sum over the marginalize_variables.
        """
        file_path = pathlib.Path(config.PROJECT_DIR, '..', 'data', 
            f'norm_{str(norm_version).zfill(2)}.npz')
        norm = np.load(file_path)
        print(norm.files)

        if len(marginalize_variables):
            raise NotImplementedError
        return

if __name__ == '__main__':
    catalog = Catalog(0)
    catalog.load()
    catalog.hist(norm_version=0)
    pass