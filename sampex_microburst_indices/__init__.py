import warnings

try:
    from sampex_microburst_indices import config
except ImportError as err:
    message = ("The sampex_microburst_indices configuration (data paths) didn't "
               "import. Did you run 'python3 -m sampex_microburst_indices init' and "
               "answer the prompts?")
    warnings.warn(message)