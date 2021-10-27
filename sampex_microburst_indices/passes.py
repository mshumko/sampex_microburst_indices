from os import name
import pathlib
import re
from datetime import datetime

import numpy as np
import pandas as pd

from sampex_microburst_indices.load.load_sampex import Load_HILT
from sampex_microburst_indices.load.load_sampex import Load_Attitude
from sampex_microburst_indices import config


class Passes:
    """
    Loop over every State 4 HILT data file and calculate all radiation belt passes.
    A radiation belt pass is defined by L-shells as the L_range kwarg.
    """
    def __init__(self, L_range=(4, 8)) -> None:
        self.L_range = sorted(L_range)
        columns = ['start_time', 'end_time', 'duration', 'MLT', 'Att_Flag']
        self.passes = pd.DataFrame(data=np.zeros((0, len(columns))), columns=columns)
        return

    def loop(self):
        """
        Loads every HILT file, load and append the corresponding attitude,
        filter by L_range, and save the passes.
        """
        self._get_hilt_file_dates()

        for date in self.hilt_dates:
            if self.in_spin_time(date):
                continue

            self.hilt = Load_HILT(date)
            self.attitude = Load_Attitude(date)
            pass
        return

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

    def _load_spin_times(self):
        """
        Load the spin_times.csv file that was used in the sampex_microburst_widths project.
        This is purely for consistency with the microburst dataset.
        """
        spin_times_path = pathlib.Path(config.PROJECT_DIR, 'data', 'spin_times.csv')
        self.spin_times = pd.read_csv(spin_times_path, parse_dates=[0,1])
        return

    def in_spin_time(self, date):
        """
        Check if date is contained between any of the start and end dates in spin_times.csv.
        """
        if not hasattr(self, 'spin_times'):
            self._load_spin_times()
        
        start_diff = np.array(
            [(date - start).total_seconds() for start in self.spin_times.loc[:, 'start']]
            )
        end_diff = np.array(
            [(date - end).total_seconds() for end in self.spin_times.loc[:, 'end']]
            )
        in_between = np.where((start_diff >=0) & (end_diff <= 0))[0]

        if len(in_between) == 0:
            return False
        elif len(in_between) == 1:
            return True
        else:
            raise ValueError('Not supposed to get here.')
        return
    


if __name__ == '__main__':
    p = Passes()
    p.loop()