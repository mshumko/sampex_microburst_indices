# sampex_microburst_indices

This project uses the microburst detected in the [sampex_microburst_widths](https://github.com/mshumko/sampex_microburst_widths) project to:

1. Quantify the absolute and relative number of microbursts observed in each outer radiation belt pass (4 < L < 8). The main quantity is the % duration of microbursts (or just the number of microbursts) in each radiation belt pass. This way the output values are 0-1 (or 0-100).
2. Add the auroral electrojet and Sym-H (i.e. the 1 minute Dst) indices to each radiation belt pass.
3. Predict the duration of microbursts given the value of the indices and their derivaties either before or during the radiation belt pass (try durations of 1 hour, 30 minutes, 15 minutes, and 5 minutes). Use a random forest model so I can quantify which variables matter for predicting the microburst occurance. 
