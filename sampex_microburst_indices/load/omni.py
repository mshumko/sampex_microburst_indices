"""
Load the OMNI data from the ftp://spdf.gsfc.nasa.gov/pub/data/omni/high_res_omni/
website
"""
import pathlib

import pandas as pd

from sampex_microburst_indices import config

omni_columns = {
    0:'Year', 1:'Day', 2:'Hour', 3:'Minute',
    37:'AE', 38:'AL', 39:'AU', 40:'SYM/D', 41:'SYM/H',
    42:'ASY/D', 43:'ASY/H'
    }

class Omni:
    def __init__(self, year) -> None:
        self.year=year
        return

    def _load_year(self):
        """
        Load a year of OMNI data
        """
        data_dir = pathlib.Path(config.PROJECT_DIR, '..', 'data')
        omni_file_paths = sorted(data_dir.rglob(f'omni*{self.year}*'))
        assert len(omni_file_paths) == 1, (
            f'{len(omni_file_paths)} OMNI files found in {data_dir.resolve()} matching "omni*{self.year}*".'
            )
        self.data2 = pd.read_csv(omni_file_paths[0], delim_whitespace=True)
        self.data = pd.read_csv(omni_file_paths[0], delim_whitespace=True, 
                                names=omni_columns.values(), usecols=omni_columns.keys())
        return

if __name__ == '__main__':
    omni = Omni(2000)
    omni._load_year()
    pass