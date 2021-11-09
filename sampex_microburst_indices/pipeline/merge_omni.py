import pathlib

import numpy as np
import pandas as pd
import progressbar

from sampex_microburst_indices import config

class Merge_OMNI:
    def __init__(self, passes_name, omni_variables=None) -> None:
        """
        Merges the OMNI data onto the radiation belt passes dataset.
        """
        self.passes_name = passes_name
        if omni_variables is None:
            self.omni_variables = ['AE', 'AL', 'AU', 'SYM/D', 'SYM/H', 'ASY/D', 'ASY/H']
        else:
            self.omni_variables = omni_variables

        self._load_passes()
        return

    def _load_passes(self):
        """
        Load the passes csv file and parse the start_time and end_time time stamps.
        """
        load_path = pathlib.Path(config.PROJECT_DIR, '..', 'data', self.passes_name)
        self.passes = pd.read_csv(load_path, parse_dates=[0,1])
        return self.passes