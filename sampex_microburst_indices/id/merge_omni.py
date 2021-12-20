import pathlib

import numpy as np
import pandas as pd

from sampex_microburst_indices import config
from sampex_microburst_indices.load import omni


class Merge_OMNI:
    def __init__(self, catalog_path, omni_columns=None):
        """
        Merges the 1-minute OMNI data to the microburst catalog.

        Parameters
        ----------
        catalog_name: str
            The filename to the microburst catalog csv file in the 
            sampex_microburst_indices/data/ folder.
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
        return

    def loop(self):
        """
        Loop over each year in the catalog and merge the omni_columns values 
        from the OMNI data sat that are within a minute.

        Parameters
        ----------
        None

        Returns
        -------
        pd.DataFrame
            The microburst catalog with the omni_columns added.
        """
        # The catalog_copy, and merged DataFrames, as well as the df.update
        # method is to incrementally merge self.catalog with each year's
        # OMNI data. If the merge is applied to self.catalog directly, it 
        # will work the for the first iteration, but then the pd.merge_asof
        # function will begin to append the overlapping column names with
        # "_x" and "_y" suffixes (see the merge_asof docs). Hence, we need to
        # apply the merge_asof function to a clean catalog and then use the 
        # changed values in catalog_copy to modify self.catalog.
        catalog_copy = self.catalog.copy()
        # Fill with Nans so the update command can update the preexisting columns. 
        # The NaN columns must be made after catalog_copy is created.
        self.catalog[self.omni_columns] = np.nan

        for year in self.unique_years:
            print(f'Merging the {year=} OMNI data.')
            self.omni = omni.Omni(year=year).load()
            merged = pd.merge_asof(
                catalog_copy, self.omni, left_index=True, 
                right_index=True, tolerance=pd.Timedelta(minutes=1),
                direction='nearest')
            self.catalog.update(merged)
        return self.catalog

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
        pd.DataFrame
            The microburst catalog.
        pd.Series
            An array of the unique years in the microburst catalog that helps the
            loop() method.
        """
        self.catalog = pd.read_csv(self.catalog_path, 
            index_col=0, parse_dates=True)
        self.unique_years = self.catalog.index.year.unique()
        return self.catalog, self.unique_years

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
        return


if __name__ == "__main__":
    m = Merge_OMNI(pathlib.Path(config.PROJECT_DIR, '..', 'data', 'microburst_catalog_00.csv' ))
    m.loop()
    m.save_catalog()