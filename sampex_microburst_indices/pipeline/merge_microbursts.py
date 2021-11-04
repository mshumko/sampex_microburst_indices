import pathlib

import numpy as np
import pandas as pd
import progressbar
# import matplotlib.pyplot as plt  # For debugging

from sampex_microburst_indices import config


class Merge_Microbursts:
    def __init__(self, passes_name, microburst_name) -> None:
        """
        Merge the passes and microburst datasets.
        """
        self.passes_name = passes_name
        self.microburst_name = microburst_name
        self._load_passes()
        self._load_microbursts()
        return
    
    def merge(self):
        """
        Count and merge the number of microbursts in self.microburst_name catalog
        with the catalog of radiation belt passes in self.passes_name.
        """
        self.passes[['microburst_count', 'total_microburst_time', 'microburst_prob']] = np.nan

        for i, row in self.passes.iterrows():
            microburst_df = self.microbursts[
                (self.microbursts.index > row['start_time']) &
                (self.microbursts.index <= row['end_time']) 
                ]
            self.passes.loc[i, 'microburst_count'] = microburst_df.shape[0]
            total_microburst_time = np.sum(np.abs(microburst_df['fwhm']))
            self.passes.loc[i, 'total_microburst_time'] = total_microburst_time
            self.passes.loc[i, 'microburst_prob'] = total_microburst_time/row['duration_s'] 
            pass
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

    def _load_passes(self):
        """
        Load the passes csv file and parse the start_time and end_time time stamps.
        """
        load_path = pathlib.Path(config.PROJECT_DIR, '..', 'data', self.passes_name)
        self.passes = pd.read_csv(load_path, parse_dates=[0,1])
        return self.passes

    def _load_microbursts(self):
        """
        Load the microburst csv file and parse the start_time and end_time time stamps.
        """
        load_path = pathlib.Path(config.PROJECT_DIR, '..', 'data', self.microburst_name)
        self.microbursts = pd.read_csv(load_path, index_col=0, parse_dates=True)
        return self.microbursts


if __name__ == '__main__':
    passes_name = 'sampex_passes_v0.csv'
    microburst_name = 'microburst_catalog.csv'
    m = Merge_Microbursts(passes_name, microburst_name)
    m.merge()
    m.save()