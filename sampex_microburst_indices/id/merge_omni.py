import pathlib
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import progressbar

from sampex_microburst_indices import config
from sampex_microburst_indices.load import omni

class Merge_OMNI:
    def __init__(self, catalog_name, omni_columns=None, mean_slope_windows_m=None) -> None:
        """
        Merges the OMNI data onto the microburst catalog.

        Parameters
        ----------
        catalog_name: str
            The filename to the microburst catalog csv file in the sampex_microburst_indices/data/ folder.
        omni_columns: list
            A list of columns to copy from the OMNI dataset. If None, it will use
            omni_columns = ['AE', 'AL', 'AU', 'SYM/D', 'SYM/H', 'ASY/D', 'ASY/H']
        mean_slope_windows_m: list
            The time lags, in minutes, to calculate the mean slope for each column in omni_columns, 
            prior to each radiation belt pass start_time. 
        """
        self.catalog_name = catalog_name
        if omni_columns is None:
            self.omni_columns = ['AE', 'AL', 'AU', 'SYM/D', 'SYM/H', 'ASY/D', 'ASY/H']
        else:
            self.omni_columns = omni_columns

        self._load_catalog()
        self.catalog[self.omni_columns] = np.nan

        if mean_slope_windows_m is not None:
            raise NotImplementedError('This basically does nothing ATM.')
            self.mean_slope_windows_m = mean_slope_windows_m

            for slope_lag in self.mean_slope_windows_m:
                for omni_column in self.omni_columns:
                    self.passes[f'{omni_column}_{slope_lag}_m_lag'] = np.nan
        return

    def _load_catalog(self):
        """
        Load the passes csv file and parse the start_time and end_time time stamps.
        """
        load_path = pathlib.Path(config.PROJECT_DIR, '..', 'data', self.catalog_name)
        self.catalog = pd.read_csv(load_path, parse_dates=True)
        return self.catalog

    def merge(self):
        """
        Loop over every radiation belt pass and append the mean indice values for
        all self.omni_columns.
        """
        current_year = datetime.min

        for i, row in progressbar.progressbar(self.catalog.iterrows(), 
                                            max_value=self.catalog.shape[0]):
            # Only load data when looping over a new year (new OMNI file).
            if row['start_time'].year != current_year:
                self.current_omni = omni.Omni(year=row['start_time'].year).load() 
                current_year = row['start_time'].year

            omni_during_pass = self.current_omni.loc[row['start_time']:row['end_time']]
            if omni_during_pass.shape[0] == 0:
                raise ValueError('Sliced OMNI data with size 0.\n{row}')
            self.passes.loc[i, self.omni_columns] = omni_during_pass[self.omni_columns].mean()
        return

    def save(self, file_name=None):
        """
        Saves the self.passes DataFrame to a csv file.
        """
        if file_name is None:
            file_name = self.passes_name

        save_path = pathlib.Path(config.PROJECT_DIR, '..', 'data', file_name)
        self.passes.to_csv(save_path, index=False)
        return


if __name__ == '__main__':
    passes_name = 'sampex_passes_v0.csv'
    mean_slope_windows_m = [15, 30, 60, 4*60]
    m = Merge_OMNI(passes_name, mean_slope_windows_m=mean_slope_windows_m)
    m.merge()
    m.save()