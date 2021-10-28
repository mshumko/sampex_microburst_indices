from os import name
import pathlib
import re
import itertools  # For debugging
from datetime import datetime

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt  # For debugging

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
        self.columns = ['start_time', 'end_time', 'duration', 'MLT', 'max_att_flag']
        self.passes = pd.DataFrame(data=np.zeros((0, len(self.columns))), columns=self.columns)
        return

    def loop(self):
        """
        Loads every HILT file, load and append the corresponding attitude,
        filter by L_range, and save the passes.
        """
        self._get_hilt_file_dates()
        attitude_dates = [datetime.min]

        for date in self.hilt_dates:
            # The following if statement is to be consistant with the 
            # microburst dataset created using the 
            # sampex_microburst_widths/microburst_id/identify_microbursts.py
            # module.
            if self.in_spin_time(date) or date.year == 1996:
                continue
            try:
                self.hilt = Load_HILT(date)
            except RuntimeError as err:
                if 'The SAMPEX HILT data is not in order.' == str(err):
                    continue
                else:
                    raise

            if date not in attitude_dates:
                # Loading the attitude will load date and future dates in that file.
                # Thus, we don't need to load the attitude data in very iteration.
                self.attitude = Load_Attitude(date)
                attitude_dates = set(self.attitude.attitude.index.date)
            
            self.merge_hilt_attitude()
            self.pass_times()
        return

    def merge_hilt_attitude(self):
        """
        Uses pd.merge_asof to merge the attitude data onto the HILT data.
        """
        self.hilt.hilt = pd.merge_asof(self.hilt.hilt, self.attitude.attitude, 
                                left_index=True, right_index=True, 
                                tolerance=pd.Timedelta(seconds=10),
                                direction='nearest')
        return

    def pass_times(self, gap_threshold_s=5*60, debug=True):
        """
        Calculate radiation belt passes by filtering by the L_Shell variable.
        """
        filtered_hilt = self.hilt.hilt[
            (self.hilt.hilt['L_Shell'] >= self.L_range[0]) &
            (self.hilt.hilt['L_Shell'] <= self.L_range[1])
            ]
        # Identify all of the start and end intervals.
        dt = (filtered_hilt.index[1:] - filtered_hilt.index[:-1]).total_seconds()
        gaps = np.where(dt > gap_threshold_s)[0]
        start_indices = np.concatenate(([0], gaps+1))
        end_indices = np.concatenate((gaps, [filtered_hilt.shape[0]-1] ))
        daily_passes = pd.DataFrame(data={col:np.zeros(len(start_indices), dtype=object)
            for col in self.columns})

        if debug:
            colors = ['r', 'g', 'b']
            color_cycler = itertools.cycle(colors)
            ax = plt.subplot()

        for i, (start_index, end_index) in enumerate(zip(start_indices, end_indices)):            
            start_time = filtered_hilt.index[start_index]
            end_time = filtered_hilt.index[end_index]
            duration_s = (end_time-start_time).total_seconds()

            if duration_s < 60:
                continue

            if debug:
                ax.scatter(filtered_hilt.index[start_index:end_index], 
                            filtered_hilt.L_Shell[start_index:end_index],
                            c=next(color_cycler))

                print(f'Pass {i} |',
                    f'L={round(filtered_hilt["L_Shell"][start_index], 1)}-{round(filtered_hilt.loc[end_time, "L_Shell"],1)} |',
                    f'MLT={round(filtered_hilt["MLT"][start_index], 1)}-{round(filtered_hilt.loc[end_time, "MLT"],1)} |',
                    f'duration={round(duration_s/60)}'
                    )

            # TODO: Add a minimum allowable pass time duration (1 minute)?
        if debug:
            plt.show()
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
        spin_times_path = pathlib.Path(config.PROJECT_DIR, '..', 'data', 'spin_times.csv')
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


if __name__ == '__main__':
    p = Passes()
    p.loop()