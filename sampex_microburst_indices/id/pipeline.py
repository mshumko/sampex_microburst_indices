import time
import pathlib

from sampex_microburst_indices.id import identify_microbursts
from sampex_microburst_indices.id import merge_attitude
from sampex_microburst_indices.id import merge_omni
from sampex_microburst_indices import config

start_time = time.time()

# Step 1: Identify microbursts using the O'Brien 2003 burst parameter method.
m = identify_microbursts.Id_Microbursts(
    baseline_width_s=0.5, foreground_width_s=0.1
    )
try:
    m.loop(debug=False)
finally:
    cat_path = m.save_catalog()

print(f'Identified microbursts in '
      f'{round((time.time()-start_time)/3600, 1)} hours')

# cat_path = pathlib.Path(config.PROJECT_DIR, '..', 'data', 'microburst_catalog_00.csv')
# Step 2: Merge the Attitude data
m = merge_attitude.Merge_Attitude(cat_path)
m.loop()
m.save_catalog()

# Step 3: Merge the minute OMNI data
m = merge_omni.Merge_OMNI(cat_path)
m.loop()
m.save_catalog()

print(f'Made the microburst catalog at {cat_path=} in '
      f'{round((time.time()-start_time)/3600, 1)} hours')