# Calculate the SAMPEX sampling time normalization for each microburst 
# catalog bin.
import pathlib

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import progressbar

from sampex_microburst_indices import config
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
        self.remove_spin_times = remove_spin_times
        self.hilt_dir = pathlib.Path(config.SAMPEX_DIR, 'hilt', 'State4')

        shape = tuple([len(vals) for _, vals in self.bins.items()])
        self.norm = np.zeros(shape, dtype=int)
        return

    def loop(self):
        """
        Loop over each HILT file, merge the attitude and OMNI data, then histogram the resulting
        data.
        """
        self._get_hilt_file_names()

        for hilt_file in progressbar.progressbar(self.hilt_files, redirect_stdout=True):
            date = self.get_filename_date(hilt_file)
            # For some reason, most of the 1996 data is useless for identifying microbursts.
            if date.year == 1996:
                continue
            # Load the data
            try:
                self.hilt_obj = sampex.Load_HILT(date)
            except RuntimeError as err:
                if "The SAMPEX HILT data is not in order" in str(err):
                    continue
                else:
                    raise
            # Resolve the 20 ms data
            self.hilt_obj.resolve_counts_state4()

            #TODO: Histogram here.
        return

    def save(self, file_name=None):
        """
        Save the normalization and bins to a numpy npy format.

        Parameters
        ----------
        file_name: str
            The npy filename. If None, will use the format morm_XX.npy where
            XX is the version number, starting at 00, and incrementing by 1 if 
            another version already exists.
        """

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

if __name__ == '__main__':
    bins = {
        'AE':np.arange(0, 2001, 100), 
        'SYM/H':np.arange(0, -201, -20),
        'L_Shell':np.arange(3, 9.1, 1),
        'MLT':np.arange(0, 24.1, 1)
    }
    n = Norm(bins)
    n.loop()