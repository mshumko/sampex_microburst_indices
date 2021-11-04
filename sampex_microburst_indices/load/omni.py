"""
Load the OMNI data from the ftp://spdf.gsfc.nasa.gov/pub/data/omni/high_res_omni/
website
"""
import pathlib
import time

import pandas as pd

from sampex_microburst_indices import config

omni_columns = {
    0:'Year', 1:'Day', 2:'Hour', 3:'Minute',
    37:'AE', 38:'AL', 39:'AU', 40:'SYM/D', 41:'SYM/H',
    42:'ASY/D', 43:'ASY/H'
    }

class Omni:
    def __init__(self, year=None, time_range=None) -> None:
        self.year=year
        self.time_range = time_range
        return

    def load(self):
        """
        Loads either a year or a time range of data.
        """
        if self.year is not None:
            self.data = self._load_year(self.year)
        elif self.time_range is not None:
            self.data = pd.DataFrame(columns=omni_columns)
            raise NotImplementedError
        else:
            raise ValueError('Neither year or time_range is passed.')
        return self.data

    def _load_year(self, verbose=False):
        """
        Load a year of OMNI data
        """
        # Find the appropriate file.
        start_time = time.time()
        data_dir = pathlib.Path(config.PROJECT_DIR, '..', 'data')
        omni_file_paths = sorted(data_dir.rglob(f'omni*{self.year}*'))
        assert len(omni_file_paths) == 1, (
            f'{len(omni_file_paths)} OMNI files found in {data_dir.resolve()} matching "omni*{self.year}*".'
            )
        # Load the OMNI csv file and parse the time stamps.
        omni_data = pd.read_csv(omni_file_paths[0], delim_whitespace=True, 
                                names=omni_columns.values(), usecols=omni_columns.keys())
        time2 = time.time()
        omni_data = self._parse_time(omni_data) 
        if verbose:                            
            print(f'OMNI load time: {round(time2-start_time)} | parse time: {round(time.time()-time2)}')   
        return omni_data

    def _parse_time(self, omni_data):
        """
        Parses the year, day, hour, and minute columns into a dateTime object.
        """
        # Merge the columns into strings so that pd.to_datetime can parse it.
        year_doy = [f'{year}-{doy} {hour}:{minute}' for year, doy, hour, minute in 
                    omni_data[['Year', 'Day', 'Hour', 'Minute']].values]
        omni_data.index = pd.to_datetime(year_doy, format='%Y-%j %H:%M')

        omni_data.drop(columns=['Year', 'Day', 'Hour', 'Minute'], inplace=True)
        return omni_data

if __name__ == '__main__':
    omni = Omni(year=2000)
    omni.load()