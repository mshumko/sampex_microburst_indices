import pathlib
from datetime import datetime

import numpy as np
import pandas as pd
import progressbar

from sampex_microburst_indices import config
from sampex_microburst_indices.load import omni

class Merge_OMNI:
    def __init__(self, passes_name, omni_variables=None) -> None:
        """
        Merges the OMNI data onto the radiation belt passes dataset.
        """
        self.passes_name = passes_name
        if omni_variables is None:
            self.omni_variables = ['AE', 'AL', 'AU', 'SYM/D', 'SYM/H', 'ASY/D', 'ASY/H']
        else:
            self.omni_variables = omni_variables

        self._load_passes()
        self.passes[self.omni_variables] = np.nan
        return

    def _load_passes(self):
        """
        Load the passes csv file and parse the start_time and end_time time stamps.
        """
        load_path = pathlib.Path(config.PROJECT_DIR, '..', 'data', self.passes_name)
        self.passes = pd.read_csv(load_path, parse_dates=[0,1])
        return self.passes

    def merge(self):
        """
        Loop over every radiation belt pass and append the mean indice values for
        all self.omni_variables.
        """
        current_year = datetime.min

        for i, row in progressbar.progressbar(self.passes.iterrows(), 
                                            max_value=self.passes.shape[0]):
            # Only load data when looping over a new year (new OMNI file).
            if row['start_time'].year != current_year:
                self.current_omni = omni.Omni(year=row['start_time'].year).load() 
                current_year = row['start_time'].year

            omni_during_pass = self.current_omni.loc[row['start_time']:row['end_time']]
            if omni_during_pass.shape[0] == 0:
                raise ValueError('Sliced OMNI data with size 0.\n{row}')
            self.passes.loc[i, self.omni_variables] = omni_during_pass[self.omni_variables].mean()
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
    m = Merge_OMNI(passes_name)
    m.merge()
    m.save()