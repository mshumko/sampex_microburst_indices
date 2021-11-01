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