from os import path
import pathlib

import pandas as pd

from sampex_microburst_indices import config

class Microbursts:
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

        if self.remove_spin_times:
            # See the docs to learn why Att_Flag = 0 or 1
            # http://www.srl.caltech.edu/sampex/DataCenter/docs/att_flag_details.txt
            self.catalog = self.catalog[
                (self.catalog.loc[:, 'Att_Flag'] == 0) |
                (self.catalog.loc[:, 'Att_Flag'] == 1)
            ]
        return self.catalog