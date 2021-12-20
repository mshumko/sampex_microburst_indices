import time

from sampex_microburst_indices.id import identify_microbursts
from sampex_microburst_indices.id import merge_attitude
from sampex_microburst_indices.id import merge_omni_2

start_time = time.time()

# # Identify microbursts using the O'Brien 2003 burst parameter method.
# m = identify_microbursts.Id_Microbursts(
#     baseline_width_s=0.5, foreground_width_s=0.1
#     )
# try:
#     m.loop(debug=False)
# finally:
#     cat_path = m.save_catalog()

# print(f'Identified microbursts in '
#       f'{round((time.time()-start_time)/3600, 1)} hours')

cat_path = '/home/mike/research/sampex_microburst_indices/data/microburst_catalog_00.csv'
# Merge the Attitude data
# m = merge_attitude.Merge_Attitude(cat_path)
# m.loop()
# m.save_catalog()

# Merge the minute OMNI data
m = merge_omni.Merge_OMNI(cat_path)
try:
    m.loop()
finally:
    m.save_catalog()

print(f'Made the microburst catalog at {cat_path=} in '
      f'{round((time.time()-start_time)/3600, 1)} hours')