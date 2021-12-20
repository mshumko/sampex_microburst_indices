"""
This module contains the Merge_AE class that uses 
pandas.merge_asof to merge the 1 minute AE cadence
values to the data. Since this module heavily relies 
on pandas, it is very efficient and the merge takes
about 10 seconds with the AE data on an HDD.
"""

import pathlib
from datetime import datetime, date

import numpy as np
import pandas as pd

from sampex_microburst_indices import config
from sampex_microburst_indices.load import omni


class Merge_OMNI:
    def __init__(self, catalog_path, omni_columns=None):
        """
        Merges the OMNI data onto the microburst catalog.

        Parameters
        ----------
        catalog_name: str
            The filename to the microburst catalog csv file in the sampex_microburst_indices/data/ folder.
        omni_columns: list
            A list of columns to copy from the OMNI dataset. If None, it will use
            omni_columns = ['AE', 'AL', 'AU', 'SYM/D', 'SYM/H', 'ASY/D', 'ASY/H']

        Returns
        -------
        None

        Example
        -------
        m = Merge_OMNI(pathlib.Path(
            config.PROJECT_DIR, '..', 'data', 'microburst_catalog_00.csv'
                    ))
        m.loop()
        m.save_catalog()    
        """
        self.catalog_path = catalog_path
        if omni_columns is None:
            self.omni_columns = ['AE', 'AL', 'AU', 'SYM/D', 'SYM/H', 'ASY/D', 'ASY/H']
        else:
            self.omni_columns = omni_columns

        self._load_catalog()
        self.catalog[self.omni_columns] = np.nan
        return

    def loop(self):
        """
        Loop over the years in the catalog and merge the omni_columns values 
        within a minute using pd.merge_asof().

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        catalog_copy = self.catalog.copy() # Keep the original to apply the merge to.

        for year in self.unique_years:
            print(f'Merging OMNI data for {year=}')
            self.omni = omni.Omni(year=year).load()
            
            merged = pd.merge_asof(
                catalog_copy, self.omni, left_index=True, 
                right_index=True, tolerance=pd.Timedelta(minutes=1),
                direction='nearest')
            self.catalog.update(merged)
        return

    def _load_catalog(self):
        """
        Load the SAMPEX catalog, parse the datetime column into datetime 
        objects, and creates a list of unique years to determine what 
        AE years to load.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        self.catalog = pd.read_csv(self.catalog_path, 
            index_col=0, parse_dates=True)
        self.unique_years = self.catalog.index.year.unique()
        return

    def save_catalog(self):
        """
        Saves the merged catalog to a csv file with the same name as 
        the loaded catalog.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        self.catalog.to_csv(self.catalog_path, index_label='dateTime')


if __name__ == "__main__":
    m = Merge_OMNI(pathlib.Path(config.PROJECT_DIR, '..', 'data', 'microburst_catalog_00.csv' ))
    m.loop()
    m.save_catalog()