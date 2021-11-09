"""
A script that shows you how to run the data processing pipeline.
"""

import passes
import merge_microbursts
import merge_omni

passes_name = 'sampex_passes_v0.csv'
microburst_name = 'microburst_catalog.csv'

# Step 1: Calculate the start and end times for all radiation belt passes.
p = passes.Passes()
p.loop()
p.save_passes(passes_name)

# Step 2: Merge microbursts 
m = merge_microbursts.Merge_Microbursts(passes_name, microburst_name)
m.merge()
m.save()

# Step3: Merge the indices.
m = merge_omni.Merge_OMNI(passes_name)
m.merge()
m.save()