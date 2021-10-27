try:
    import config
except ImportError:
    print("The sampex_microburst_indices configuration (data paths) didn't "
          "import. Did you run python3 -m sampex_microburst_indices init and "
          "answer the prompts?")