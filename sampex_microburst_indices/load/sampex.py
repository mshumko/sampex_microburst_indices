# This program loads the HILT data and parses it into a nice format
import argparse
import pathlib
import zipfile
import re
from datetime import datetime, date

import pandas as pd
import numpy as np

from sampex_microburst_indices import config


class Load_HILT:
    def __init__(self, load_date, extract=False, 
                time_index=True, verbose=False):
        """
        Load the HILT data given a date. If this class will look for 
        a file with the "hhrrYYYYDOY*" filename pattern and open the 
        found csv file. If the file is zipped, it will first be unzipped. 
        If you want to extract the file as well, set extract=True.
        time_index=True sets the time index of self.hilt to datetime objects
        otherwise the index is just an enumerated list.
        """
        self.load_date = load_date
        self.load_date_str = date2yeardoy(self.load_date)
        self.verbose = verbose

        # Get the filename and search for it. If multiple or no
        # unique files are found this will raise an assertion error.
        file_name_glob = f'hhrr{self.load_date_str}*'
        matched_files = list(
            pathlib.Path(config.SAMPEX_DIR, 'hilt').rglob(file_name_glob)
            )
        # 1 if there is just one file, and 2 if there is a file.txt and 
        # file.txt.zip files.
        assert len(matched_files) in [1, 2], (f'{len(matched_files)} matched HILT files found.'
                                        f'\nSearch string: {file_name_glob}'
                                        f'\nSearch directory: {pathlib.Path(config.SAMPEX_DIR, "hilt")}'
                                        f'\nmatched files: {matched_files}')
        self.file_path = matched_files[0]

        # Load the zipped data and extract if a zip file was found.
        if self.file_path.suffix == 'zip':
            self.read_zip(self.file_path, extract=extract)
        else:
            self.read_csv(self.file_path)

        # Parse the seconds of day time column to datetime objects
        self.parse_time(time_index=time_index)
        return
        
    def read_zip(self, zip_path, extract=False):
        """
        Open the zip file and load in the csv file. If extract=False than the file
        will only be opened and not extracted to a text file in the 
        sampex/data/hilt directory. 
        """
        txt_name = zip_path.stem # Remove the .zip from the zip_path
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            if extract:
                zip_ref.extractall(zip_path.parent)
                #self.hilt = pd.read_csv(zip_path.parent / txt_name)
                self.read_csv(zip_path.parent / txt_name)
            else:
                with zip_ref.open(txt_name) as f:
                    # self.hilt = pd.read_csv(f, sep=' ')
                    self.read_csv(f)
        return
    
    def read_csv(self, path):
        """
        Reads in the CSV file given either the filename or the 
        zip file reference
        """
        if self.verbose:
            print(f'Loading SAMPEX HILT data from {self.load_date.date()} from {path.name}')
        self.hilt = pd.read_csv(path, sep=' ')
        return

    def parse_time(self, time_index=True):
        """ 
        Parse the seconds of day column to a datetime column. 
        If time_index=True, the time column will become the index.
        """
        # Check if the seconds are monotonically increasing.
        np_time = self.hilt['Time'].to_numpy()
        if np.any(np_time[1:] < np_time[:-1]):
            raise RuntimeError(f'The SAMPEX HILT data is not in order for {self.load_date_str}.')
        # Convert seconds of day to a datetime object.
        day_seconds_obj = pd.to_timedelta(self.hilt['Time'], unit='s')
        self.hilt['Time'] = pd.Timestamp(self.load_date.date()) + day_seconds_obj
        if time_index:
            self.hilt.index = self.hilt['Time']
            del(self.hilt['Time'])
        return

    def resolve_counts_state4(self):
        """ 
        This function resolves the HILT counts to 20 ms resolution assuming 
        the data is in state4. The counts represent the sum from the 4 SSDs.
        Data saved in self.hilt_resolved
        """ 
        resolution_ms = 20E-3
        # Resolve the counts using numpy (most efficient way with 
        # static memory allocation)
        self.counts = np.nan*np.zeros(5*self.hilt.shape[0], dtype=int)
        for i in [0, 1, 2, 3]:
            self.counts[i::5] = self.hilt[f'Rate{i+1}']
        # This line is different because rate5 is 100 ms SSD4 data.
        self.counts[4::5] = self.hilt['Rate6'] 

        # Resolve the time array.
        self.times = np.nan*np.zeros(5*self.hilt.shape[0], dtype=object)
        for i in [0, 1, 2, 3, 4]:
            self.times[i::5] = self.hilt.index + pd.to_timedelta(resolution_ms*i, unit='s')

        self.hilt_resolved = pd.DataFrame(data={'counts':self.counts}, index=self.times)
        return self.counts, self.times


class Load_PET:
    def __init__(self, load_date, verbose=False) -> None:
        self.load_date = load_date
        self.load_date_str = date2yeardoy(self.load_date)
        self.verbose = verbose
        return

    def load_pet(self):
        """
        Loads the PET data into self.data.
        """
        pet_path = self._find_file(self.load_date)
        self.data = pd.read_csv(pet_path, sep=' ')
        self.parse_time()
        return self.data

    def parse_time(self, time_index=True):
        """ 
        Parse the seconds of day column to a datetime column. 
        If time_index=True, the time column will become the index.
        """
        # Check if the seconds are monotonically increasing.
        np_time = self.data['Time'].to_numpy()
        if np.any(np_time[1:] < np_time[:-1]):
            raise RuntimeError(f'The SAMPEX PET data is not in order for {self.load_date_str}.')
        # Convert seconds of day to a datetime object.
        day_seconds_obj = pd.to_timedelta(self.data['Time'], unit='s')
        self.data['Time'] = pd.Timestamp(self.load_date.date()) + day_seconds_obj
        if time_index:
            self.data.index = self.data['Time']
            del(self.data['Time'])
        return

    def _find_file(self, day):
        """
        Recursively searches the config.SAMPEX_DIR/pet/ directory for the file.
        """
        file_name_glob = f'phrr{self.load_date_str}*'
        matched_files = list(
            pathlib.Path(config.SAMPEX_DIR, 'pet').rglob(file_name_glob)
            )
        # 1 if there is just one file, and 2 if there is a file.txt and 
        # file.txt.zip files.
        assert len(matched_files)==1, (f'{len(matched_files)} matched PET files found.'
                                        f'\nSearch string: {file_name_glob}'
                                        f'\nSearch directory: {pathlib.Path(config.SAMPEX_DIR, "pet")}'
                                        f'\nmatched files: {matched_files}')
        return matched_files[0]


class Load_LICA:
    def __init__(self, load_date, verbose=False) -> None:
        self.load_date = load_date
        self.load_date_str = date2yeardoy(self.load_date)
        self.verbose = verbose
        return

    def load_lica(self):
        """
        Loads the LICA data into self.data.
        """
        lica_path = self._find_file(self.load_date)
        self.data = pd.read_csv(lica_path, sep=' ')
        self.parse_time()
        return self.data

    def parse_time(self, time_index=True):
        """ 
        Parse the seconds of day column to a datetime column. 
        If time_index=True, the time column will become the index.
        """
        # Check if the seconds are monotonically increasing.
        np_time = self.data['Time'].to_numpy()
        if np.any(np_time[1:] < np_time[:-1]):
            raise RuntimeError(f'The SAMPEX LICA data is not in order for {self.load_date_str}.')
        # Convert seconds of day to a datetime object.
        day_seconds_obj = pd.to_timedelta(self.data['Time'], unit='s')
        self.data['Time'] = pd.Timestamp(self.load_date.date()) + day_seconds_obj
        if time_index:
            self.data.index = self.data['Time']
            del(self.data['Time'])
        return

    def _find_file(self, day):
        """
        Recursively searches the config.SAMPEX_DIR/pet/ directory for the file.
        """
        file_name_glob = f'lhrr{self.load_date_str}*'
        matched_files = list(
            pathlib.Path(config.SAMPEX_DIR, 'lica').rglob(file_name_glob)
            )
        # 1 if there is just one file, and 2 if there is a file.txt and 
        # file.txt.zip files.
        assert len(matched_files)==1, (f'{len(matched_files)} matched LICA files found.'
                                        f'\nSearch string: {file_name_glob}'
                                        f'\nSearch directory: {pathlib.Path(config.SAMPEX_DIR, "lica")}'
                                        f'\nmatched files: {matched_files}')
        return matched_files[0]


class Load_Attitude:
    def __init__(self, load_date, verbose=False):
        """ 
        This class loads the appropriate SAMEX attitude file, 
        parses the complex header and converts the time 
        columns into datetime objects
        """
        self.load_date = load_date
        self.load_date_str = date2yeardoy(load_date)
        self.verbose = verbose

        # Find the appropriate attitude file.
        self.find_matching_attitude_file()

        # Load the data into a dataframe
        self.load_attitude()
        return

    def find_matching_attitude_file(self):
        """ 
        Uses pathlib.rglob to find the attitude file that contains 
        the DOY from self.load_date
        """
        attitude_files = sorted(list(pathlib.Path(config.SAMPEX_DIR, 'attitude').rglob('PSSet_6sec_*_*.txt')))
        start_end_dates = [re.findall(r'\d+', str(f.name))[1:] for f in attitude_files]
        
        current_date_int = int(self.load_date_str)
        self.attitude_file = None

        for f, (start_date, end_date) in zip(attitude_files, start_end_dates):
            if (int(start_date) <= current_date_int) and (int(end_date) >= current_date_int):
                self.attitude_file = f
        if self.attitude_file is None:
            raise ValueError(f'A matched file not found in {pathlib.Path(config.SAMPEX_DIR, "attitude")} '
                             f'for YEARDOY={self.load_date_str}')
        return self.attitude_file

    def load_attitude(self, columns='default', remove_old_time_cols=True):
        """ 
        Loads the attitude file. Only columns specified in the columns arg are 
        loaded to conserve memory. The year, day_of_year, and sec_of_day columns
        are used to construct a list of datetime objects that are assigned to
        self.attitude index. 

        If remove_old_time_cols is True, the year, DOY, and second columns are 
        delited to conserve memory.
        """
        if self.verbose:
            print(f'Loading SAMPEX attitude data from {self.load_date.date()} from'
                f' {self.attitude_file.name}')
        # A default set of hard-coded list of columns to load
        if columns=='default':
            columns = {
                0:'Year', 1:'Day-of-year', 2:'Sec_of_day', 6:'GEO_Radius',
                7:'GEO_Long', 8:'GEO_Lat', 9:'Altitude', 20:'L_Shell',
                22:'MLT', 42:'Mirror_Alt', 68:'Pitch', 71:'Att_Flag'
            }
        # Open the attitude file stream
        with open(self.attitude_file) as f:
            # Skip the long header until the "BEGIN DATA" line 
            self._skip_header(f)
            # Save the rest to a file using columns specified by the columns.keys() with the 
            # columns values for the column names.
            self.attitude = pd.read_csv(f, delim_whitespace=True,
                                        names=columns.values(), 
                                        usecols=columns.keys())
        self._parse_attitude_datetime(remove_old_time_cols)
        return

    def _skip_header(self, f):
        """ 
        Read in the "f" attitude file stream line by line until the 
        "BEGIN DATA" line is reached. Then return the row index to the
        names from the parsed header.
        """
        for i, line in enumerate(f):
            if "BEGIN DATA" in line:
                # because for some reason the first attitude row has 
                # an extra column so skip the first "normal" row.
                next(f) 
                return 
        return None

    def _parse_attitude_datetime(self, remove_old_time_cols):
        """
        Parse the attitude year, DOY, and second of day columns 
        into datetime objects. 
        """
        # Parse the dates by first making YYYY-DOY strings.
        year_doy = [f'{year}-{doy}' for year, doy in 
                    self.attitude[['Year', 'Day-of-year']].values]
        # Convert to date objects
        attitude_dates=pd.to_datetime(year_doy, format='%Y-%j')
        # Now add the seconds of day to complete the date and time.
        self.attitude.index = attitude_dates + pd.to_timedelta(self.attitude['Sec_of_day'], unit='s')
        # Optionally remove duplicate columns to conserve memory.
        if remove_old_time_cols:
            self.attitude.drop(['Year', 'Day-of-year', 'Sec_of_day'], axis=1, inplace=True)
        return


def date2yeardoy(day):
    """ 
    Converts a date in a string, datetime.datetime or a pd.Timestamp format into a
    "YYYYDOY" string that are used for the SAMPEX names.
    """
    if isinstance(day, str):
        day = pd.to_datetime(day)
    
    # Figure out how to calculate the day of year (DOY)
    if isinstance(day, pd.Timestamp):
        doy = str(day.dayofyear).zfill(3)
    elif isinstance(day, (datetime, date)):
        doy = str(day.timetuple().tm_yday).zfill(3)
    return f'{day.year}{doy}'

def yeardoy2date(yeardoy):
    """
    Converts a date in the year day-of-year format (YEARDOY)
    into a datetime.datetime object.
    """
    return datetime.strptime(yeardoy, "%Y%j")

if __name__ == '__main__':
    import matplotlib.pyplot as plt

    day = datetime(2007, 1, 20)

    p = Load_PET(day)
    p.load_pet()

    h = Load_HILT(day)
    h.resolve_counts_state4()
    # a = Load_Attitude(day)

    l = Load_LICA(day)
    l.load_lica()

    fig, ax = plt.subplots(3, sharex=True)
    ax[0].step(h.hilt_resolved.index, h.hilt_resolved.counts, label='HILT', where='post')
    ax[1].step(p.data.index, p.data['P1_Rate'], label='PET', where='post')
    ax[2].step(l.data.index, l.data['Stop'], label='LICA/Stop', where='post')

    ax[0].set(ylabel='HILT')
    ax[1].set(ylabel='PET')
    ax[2].set(ylabel='LICA/Stop')
    ax[-1].set_xlabel('Time')

    plt.suptitle(f'SAMPEX | {day.date()}')
    plt.show()