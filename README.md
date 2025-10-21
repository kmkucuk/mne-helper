# pyeeg: EEG Data Processing Pipeline

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
  preprocess/       # filtering, re-referencing, artifact handling
  features/         # temporal, spectral, spatial features
  models/           # training, inference, evaluation
  visualization/    # plotting utilities
  pipeline/         # orchestration scripts and steps
scripts/            # CLI helpers for common tasks
tests/              # unit tests mirroring modules
data/               # raw/interim/processed/external (gitignored)
```

## Quickstart

- Download data:
```bash
python scripts/download_data.py
```

- Preprocess and extract features:
```bash
python scripts/run_preprocess.py
python scripts/extract_features.py
```

- Train and evaluate a model:
```bash
python scripts/train_model.py
python scripts/evaluate_model.py
```

## Testing

```bash
pytest
```

## License

This project is licensed under the terms of the MIT license.

# pyeeg
