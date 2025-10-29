# mne-helper: EEG Data Processing Pipeline

A modular Python pipeline for EEG data I/O, preprocessing, feature extraction, modeling, and evaluation. 

## Installation

1. Create a virtual environment and activate it.
2. Install the project in editable mode:

```bash
pip install -e .
```

Optional: install dev tools and pre-commit hooks:

```bash
pip install pre-commit ruff
pre-commit install
```

## Project Structure

```
src/pyeeg/
  config/           # configuration management
  io/               # loaders/writers for EEG data
  preprocess/       # EEG auto-montage selection, segmentation
  signal/           # time-frequency decomposition
  modeling/         # Bayesian & ANN classification of EEG features (coming soon)
scripts/            # CLI helpers for common tasks
tests/              # unit tests mirroring modules
data/               # raw/interim/processed/external (gitignored)
```


## License

This project is licensed under the terms of the MIT license.

# pyeeg
