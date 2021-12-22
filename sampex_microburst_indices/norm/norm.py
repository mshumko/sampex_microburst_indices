# Calculate the SAMPEX sampling time normalization for each microburst 
# catalog bin.
import pathlib
import re

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import progressbar

from sampex_microburst_indices import config
from sampex_microburst_indices.load import omni
from sampex_microburst_indices.load import sampex


class Norm:
    def __init__(self, bins, remove_spin_times=True):
        """
        Calculate the number of samples that HILT took data in bins.

        Parameters
        ----------
        bins: dict
            A dictionary of lists (or 1d arrays) that specify the bins along each variable.
            The bins are passed into numpy.histogramdd.
        remove_spin_times: bool
            A flag to keep or remove microbursts taken when SAMPEX was in the spin mode,
            when Att_Flag >= 100.
        """
        self.bins = bins
        # Check that each bin is monotonically increasing for numpy.histogramdd()
        for key, val in self.bins.items():
            if any(np.diff(val) < 0):
                self.bins[key] = sorted(val)

        self.remove_spin_times = remove_spin_times
        self.hilt_dir = pathlib.Path(config.SAMPEX_DIR, 'hilt', 'State4')

        shape = tuple([len(vals)-1 for _, vals in self.bins.items()])
        self.norm_s = np.zeros(shape, dtype=int)
        return

    def loop(self):
        """
        Loop over each HILT file, merge the attitude and OMNI data, then histogram the resulting
        data.
        """
        self._get_hilt_file_names()

        for hilt_file in progressbar.progressbar(self.hilt_files, redirect_stdout=True):
            date = self._get_filename_date(hilt_file)
            # For some reason, most of the 1996 data is useless for identifying microbursts,
            # so we ignore that year here too.
            if date.year == 1996:
                continue

            try:
                self._load_and_merge_data(date)  # The HILT, Attitude, and OMNI datasets.
            except (RuntimeError, ValueError) as err:
                if "The SAMPEX HILT data is not in order" in str(err):
                    continue
                elif ('A matched file not found in' in str(err)) and (date.date() == pd.Timestamp(2012, 11, 6)):
                    continue  # pd.Timestamp(2012, 11, 6) date doesn't have an attitude file.
                else:
                    raise    
            self._hist_hilt()
        return

    def save(self, file_name=None):
        """
        Save the normalization and bins to a numpy npz archive. Read the archive
        with np.lead() which will return a dictionary-like object.

        Parameters
        ----------
        file_name: str
            The npy filename. If None, will use the format norm_XX.npy where
            XX is the version number, starting at 00, and incrementing by 1 if 
            another version already exists.
        """
        if file_name is None:
            counter = 0
            while True:
                save_path = pathlib.Path(config.PROJECT_DIR, '..', 'data',
                    'norm_{:02d}.npz'.format(counter))
                if not save_path.exists():
                    break
                counter += 1
        else:
            save_path = pathlib.Path(config.PROJECT_DIR, '..', 'data', file_name)

        save_dict = self.bins.copy()
        save_dict['norm'] = self.norm_s
        np.savez(save_path, **save_dict)
        return

    def _get_hilt_file_names(self):
        """
        Get a sorted list of file names in the State4 directory
        """
        hilt_files_generator = self.hilt_dir.glob('*')
        self.hilt_files = sorted(list(hilt_files_generator))
        if len(self.hilt_files) == 0:
            raise FileNotFoundError('No HILT files found. Is the data directory avaliable '
                                    'and defined in config.SAMPEX_DIR?')
        return

    def _get_filename_date(self, file_path):
        """ Given a filename find the date using regex and pd.to_datetime"""
        file_name = file_path.name
        # Pick off the numbers out of the filename.
        year_doy_str = re.findall(r'\d+', str(file_name))[0]
        # Parse the date assuming a YYYYDOY format.
        return pd.to_datetime(year_doy_str, format='%Y%j')

    def _load_and_merge_data(self, date):
        """
        Loads the SAMPEX HILT and Attitude data and the OMNI data. Then it 
        merges the Attitude and OMNI data to HILT and returns the merged 
        pd.DataFrame.
        """
        # Here, each time stamp is 0.1 seconds instead of 20 ms as when I call 
        # self.hilt_obj.resolve_counts_state4()
        self.hilt_obj = sampex.Load_HILT(date)
        self.hilt = self.hilt_obj.hilt

        # Load the Attitude data
        if ((not hasattr(self, 'attitude')) or 
            (self.attitude.attitude[self.attitude.attitude.index.date == date].shape[0] == 0)):

            print(f'Loading attitude file for {date.date()}')
            self.attitude = sampex.Load_Attitude(date)

        # Merge attitude to HILT
        self.hilt = pd.merge_asof(self.hilt, self.attitude.attitude, 
            left_index=True, right_index=True, tolerance=pd.Timedelta(seconds=6),
            direction='nearest')

        # Load and merge OMNI to HILT
        if ((not hasattr(self, 'omni')) or 
            (self.omni[self.omni.index.year == date.year].shape[0] == 0)):

            print(f'Loading OMNI file for {date.date()}')
            self.omni = omni.Omni(date.year).load()

        self.hilt = pd.merge_asof(
            self.hilt, self.omni, left_index=True, 
            right_index=True, tolerance=pd.Timedelta(minutes=1),
            direction='nearest')

        # Apply the same attitude and nan filters as Catalog() in catalog.py
        self.hilt.dropna(inplace=True)
        if self.remove_spin_times:
            # See the docs to learn why Att_Flag = 0 or 1
            # http://www.srl.caltech.edu/sampex/DataCenter/docs/att_flag_details.txt
            self.hilt = self.hilt[
                (self.hilt.loc[:, 'Att_Flag'] == 0) |
                (self.hilt.loc[:, 'Att_Flag'] == 1)
            ]
        return

    def _hist_hilt(self):
        """
        The Norm magic happens here.
        """    
        H, _ = np.histogramdd(
            self.hilt.loc[:, self.bins.keys()].to_numpy(),
            bins=list(self.bins.values())
        )
        # Divide by 10 so self.norm_s is in units of seconds...because each time stamp is 0.1 s.
        self.norm_s += (H/10).astype(int)
        return


if __name__ == '__main__':
    bins = {
        'L_Shell':np.arange(3, 9.1, 1),
        'MLT':np.arange(0, 24.1, 1),
        'AE':np.arange(0, 2001, 100), 
        'SYM/H':np.arange(-200, 61, 20)
    }
    n = Norm(bins)
    n.loop()
    n.save()