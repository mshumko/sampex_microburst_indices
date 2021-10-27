"""
Loop over every State 4 HILT data file and calculate all radiation belt passes.
A radiation belt pass is defined by 4 < L < 8.
"""
import pathlib
import re
from datetime import date, datetime

import numpy as np
import pandas as pd

import sampex_microburst_indices.config as config

class Passes:
    def __init__(self) -> None:
        pass

    def _get_hilt_file_paths(self):
        """
        Search for and return all HILT files matching 'hhrr*.txt*' in the 
        config.SAMPEX_DIR/hilt/State4/ directory.
        """
        hilt_file_paths_gen = pathlib.Path(config.SAMPEX_DIR, 'hilt', 'State4').rglob('hhrr*.txt*')
        self.hilt_file_paths = sorted(hilt_file_paths_gen)
        if len(self.hilt_file_paths) == 0:
            raise FileNotFoundError(f'No HILT files found in {config.SAMPEX_DIR}.')
        return self.hilt_file_paths

    def _get_hilt_file_dates(self):
        """
        Search for and parse dates of all HILT files matching 'hhrr*.txt*' in the 
        config.SAMPEX_DIR/hilt/State4/ directory.
        """
        self._get_hilt_file_paths()

        date_strings = [re.search(r'\d+', t.name).group() for t in self.hilt_file_paths]
        self.hilt_dates = [datetime.strptime(t, "%Y%j") for t in date_strings]
        return self.hilt_dates

if __name__ == '__main__':
    p = Passes()
    hilt_dates = p._get_hilt_file_dates()
    print(hilt_dates, len(hilt_dates))
    pass