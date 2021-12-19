import pathlib
import re
import subprocess

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import progressbar

from sampex_microburst_indices import config
from sampex_microburst_indices.load import sampex
from sampex_microburst_indices.id import signal_to_background

class Id_Microbursts:
    def __init__(self, baseline_width_s=0.500, foreground_width_s=0.1,
                threshold=10):
        self.hilt_dir = pathlib.Path(config.SAMPEX_DIR, 'hilt', 'State4')
        self.baseline_width_s = baseline_width_s
        self.foreground_width_s = foreground_width_s
        self.threshold = threshold
        return

    def loop(self, debug=False):
        """
        Loop over the HILT files and run the following steps:
        - get the date from the file name,
        - load and resolve the 20 ms HILT file,
        - Run the microburst detection code on it, and
        - save to self.microbursts.
        """
        self.get_file_names()
        self.microburst_times = pd.DataFrame(data=np.zeros((0, 2)), 
                                            columns=['dateTime', 'burst_param'])

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

            # Use the hilt data to id microbursts  
            try:
                self.id_microbursts(debug=debug)
            except ValueError as err:
                if str(err) == 'No detections found':
                    print(err, hilt_file.name)
                    continue
                else:
                    raise
            # self.test_detections()
        return

    def get_file_names(self):
        """
        Get a sorted list of file names in the State4 directory
        """
        hilt_files_generator = self.hilt_dir.glob('*')
        self.hilt_files = sorted(list(hilt_files_generator))
        if len(self.hilt_files) == 0:
            raise FileNotFoundError('No HILT files found. Is the data directory avaliable '
                                    'and defined in config.SAMPEX_DIR?')
        return

    def get_filename_date(self, file_path):
        """ Given a filename find the date using regex and pd.to_datetime"""
        file_name = file_path.name
        # Pick off the numbers out of the filename.
        year_doy_str = re.findall(r'\d+', str(file_name))[0]
        # Parse the date assuming a YYYYDOY format.
        return pd.to_datetime(year_doy_str, format='%Y%j')

    def id_microbursts(self, debug=False):
        """ Use SignalToBackground class to identify microbursts """
        self.stb = signal_to_background.SignalToBackground(
                                    self.hilt_obj.counts, 20E-3, 
                                    self.baseline_width_s,
                                    foreground_width_s=self.foreground_width_s)
        self.stb.significance()
        self.stb.find_microburst_peaks(std_thresh=self.threshold)

        # Remove detections made near data gaps (where the baseline is invalid)
        self.remove_detections_near_time_gaps()

        # Save to a DataFrame
        df = pd.DataFrame(
            data={
                'dateTime':self.hilt_obj.hilt_resolved.iloc[self.stb.peak_idt, :].index,
                'burst_param':np.round(self.stb.n_std.values[self.stb.peak_idt].flatten(), 1)
                },
            index=self.stb.peak_idt
            )
        self.microburst_times = pd.concat([self.microburst_times, df])

        if debug:
            self.test_detections()
        return

    def remove_detections_near_time_gaps(self):
        """

        """
        times = self.hilt_obj.hilt_resolved.index
        dt = (times[1:] - times[:-1]).total_seconds()
        bad_indices = np.array([])
        bad_index_range = int(5/(dt[0]*2))
        # Loop over every peak and check that the nearby data has no
        # time gaps longer than 1 second.
        for i, peak_i in enumerate(self.stb.peak_idt):
            if dt[peak_i-bad_index_range:peak_i+bad_index_range].max() > 1:
                bad_indices = np.append(bad_indices, i)
        self.stb.peak_idt = np.delete(self.stb.peak_idt, bad_indices.astype(int))
        return

    def save_catalog(self, save_name=None):
        """ 
        Saves the microburst_times DataFrame to a csv file 
        with the save_name filename. If save_name is none,
        a default catalog name will be used:
        'microburst_catalog_###.csv', where ### is a verion 
        counter, starting from 0. If a filename already exists,
        the counter increments and checks if that filename 
        already exists.

        This method also saves the creation time, catalog name,
        and git revision hash to catalog_log.csv also in the
        data subdirectory.
        """
        # Drop duplicate detections, if any
        pre_len = self.microburst_times.shape[0]
        self.microburst_times.drop_duplicates(subset='dateTime', inplace=True)
        print(f'{pre_len - self.microburst_times.shape[0]} duplicate detections dropped.')
        # If the save_name is None, save to a default filename
        # that gets incremented if it already exists.
        if save_name is None:
            counter = 0
            while True:
                save_path = pathlib.Path(config.PROJECT_DIR, '..', 'data',
                    'microburst_catalog_{:02d}.csv'.format(counter))
                if not save_path.exists():
                    break
                counter += 1
        else:
            save_path = pathlib.Path(config.PROJECT_DIR, '..', 'data', save_name)

        # Save the microburst catalog
        log_path = pathlib.Path(config.PROJECT_DIR, '..', 'data', 'catalog_log.csv')
        self.microburst_times.to_csv(save_path, index=False)

        # Log the saved catalog info.
        git_revision_hash = subprocess.check_output(
            ['git', 'rev-parse', 'HEAD']
            ).strip().decode()
        log = pd.DataFrame(
            index=[0],
            data={ 
                'time':pd.Timestamp.today(),
                'catalog_name':save_path.name,
                'burst_params':repr(self),
                'git_revision_hash':git_revision_hash
                })
        # Determine if the header needs to be written
        if log_path.exists():
            header=False
        else:
            header=True
        log.to_csv(log_path, 
                mode='a', header=header, index=False)
        return save_path

    def test_detections(self):
        """ This method plots the microburst detections """
        # plt.plot(pd.Series(self.hilt_obj.times), self.hilt_obj.counts, 'k') 
        plt.plot(pd.Series(self.hilt_obj.times), self.hilt_obj.counts, 'k') 
        plt.scatter(pd.Series(self.hilt_obj.times[self.stb.peak_idt]), 
                    self.hilt_obj.counts[self.stb.peak_idt], 
                    c='r', marker='D')
        plt.show()

    def __repr__(self):
        params = (f'baseline_width_s={self.baseline_width_s}, '
                  f'foreground_width_s={self.foreground_width_s}, '
                  f'threshold={self.threshold}')
        return f'{self.__class__.__qualname__}(' + params + ')'