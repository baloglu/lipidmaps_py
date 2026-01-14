# lipidmaps_py

A Python package providing tools to ingest, normalize, validate, and manage lipidomics datasets and to interface with LIPID MAPS resources.

This project is intended for researchers and developers working with mass-spectrometry lipidomics data who need reproducible preprocessing (ingestion, normalization, and QC), integration with RefMet identifiers, and programmatic access to dataset management utilities.

## Purpose

- Provide robust CSV/TSV ingestion with flexible column handling and format detection.
- Normalize lipid names to RefMet where possible so downstream analyses work with standardized identifiers.
- Validate datasets and generate concise QC reports highlighting missing values, format inconsistencies, and common data issues.
- Offer a `DataManager` abstraction for working with quantified lipids, samples, and simple cohort metadata.
- Lay the groundwork for LIPID MAPS API integration (LM ID lookup) and reaction-analysis features.

## Development Status

### ✅ Complete
- **Data Import & Validation**: CSV/TSV data ingestion with format detection
- **Data Normalization**: RefMet standardization
- **Quality Control**: Data validation and issue reporting
- **Data Management**: DataManager for handling quantified lipid datasets
- **Sample Metadata**: Support for experimental metadata and conditions

### 🚧 In Progress
- **LIPID MAPS API Integration**: LM ID lookup and validation
- **Reaction Analysis**: Integration with LIPID MAPS reactions database

## Installation

### Prerequisites
- Python 3.9 or higher

> **Note**: Test functions require sqlite3 support in python. If you encounter `ModuleNotFoundError: No module named '_sqlite3'`, your Python installation was built without SQLite support. Either:
> - Use your system's Python (e.g., `python3` instead of a custom-built Python)
> - Rebuild Python with SQLite development libraries installed (`sudo dnf install sqlite-devel` on AlmaLinux/Fedora/RHEL, then rebuild Python)

### Install from Source

1. Clone the repository:
```bash
git clone https://github.com/s-andrews/lipidmaps_py.git
cd lipidmaps_py
```

2. Create a virtual environment (recommended):
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install the package:
```bash
pip install .
```

or to include dev requirements
```bash
pip install -e .[dev]
```

4. Install development dependencies (optional and if you haven't already used .[dev], for running tests):
```bash
pip install pytest pytest-cov pytest-html black flake8 mypy
```

### Verify Installation

Test that the package is correctly installed:
```bash
python -c "import lipidmaps; print('Installation successful')"
```

## Running Tests & Reports

The package ships with a comprehensive pytest configuration (`pytest.ini`) that automatically:

- Runs tests in `importlib` mode (fixes relative-import issues)
- Collects coverage for the `lipidmaps` package
- Writes a terminal coverage summary and an HTML coverage site (`htmlcov/index.html`)
- Generates a standalone HTML test report (`report.html`) you can archive or share

Running the full suite is therefore as simple as:

```bash
# Inside the repo (venv recommended)
pytest
```

### Targeted Test Runs

```bash
# Verbose output
pytest -v

# Specific directory or file
pytest tests/data/
pytest tests/data/test_csv_ingestion.py

# Disable reporting add-ons if you need a quicker loop
PYTEST_ADDOPTS="" pytest -q
```

### Viewing Reports

- **Test results**: open `report.html` in any browser for per-test details, logs, and attachments.
- **Coverage**: open `htmlcov/index.html` for annotated source along with percentage metrics.
- Both artifacts are produced on every `pytest` run locally and in CI (uploaded as workflow artifacts).

## Quick Start

### Basic Usage

```python
from lipidmaps.data.data_manager import DataManager

# Create a DataManager instance
manager = DataManager()

# Load a CSV file. The package includes sample datasets in the `tests/data/inputs/` directory:
dataset = manager.process_csv("path/to/your/data.csv")

# Csv file is processed into an object with iterable samples and lipids data
# samples - the list of SampleMetadata type objects with sample_id, group and label attributes
print(dataset.samples[:1]) 

# lipids - the list of QuantifiedLipid type objects with input_name, standardized_name, lm_id, recognized and values object "sample_id": "value"
print(dataset.lipids[:1]) 

# List first 5 samples 
print(f"Samples: {dataset.list_samples()[:5]}")

# List first 5 lipids
print(f"Lipids: {dataset.list_lipids()[:5]}")

# Update LIPID MAPS ids by headgroups
# fill_missing_lm_ids_from_headgroups(dataset) will assign headgroup LIPID MAPS ids to lipids and return the updated count.
updated_count = manager.fill_missing_lm_ids_from_headgroups(dataset)

# List lipid names where an lm id is assigned
print(f"Lipid names with assigned lm ids: {dataset.list_lipids_with_lmid()[:5]}")

# Find lipids by name. This function will return array of lipid objects where query is found within input_name or standard_name 
queried_lipids = dataset.find_lipids("query")


```

## Example Datasets

Sample datasets are available in `tests/data/inputs/`:
- `small_demo.csv`: Small example dataset for quick testing
- `large_demo.csv`: Larger dataset for comprehensive testing

## Documentation

For more detailed documentation, see:
- `docs/custom_columns_guide.md`: Guide for working with custom data columns
- `INSTALL.md`: Detailed installation instructions

## Project Structure

```
lipidmaps_py/
├── src/lipidmaps/           # Main package code
│   ├── data/                # Data analysis module
│   │   ├── models/         # Data models
│   │   ├── ingestion/      # Data import
│   │   ├── validation/     # Data validation
│   │   └── config/         # Configuration
│   └── tools/              # Utility tools
├── tests/                   # Test suite
│   └── data/               # Data module tests
│       └── inputs/         # Sample datasets
└── docs/                    # Documentation
```

## Troubleshooting

### SQLite3 Module Not Found

If you get `ModuleNotFoundError: No module named '_sqlite3'`:

1. **Use system Python** instead of custom-built Python:
   ```bash
   /usr/bin/python3 -m venv venv # or /bin/python3 
   source venv/bin/activate
   pip install -e .
   ```

2. **Or rebuild Python with SQLite support**:
   ```bash
   sudo dnf install sqlite-devel  # CentOS/RHEL
   # Then rebuild and reinstall Python from source
   ```

### Import Errors

If you get import errors, make sure the package is installed:
```bash
pip install -e .
```

### Test Failures

If tests fail, ensure you have all dependencies:
```bash
pip install pytest pandas numpy requests
```

## Contributing

Contributions are welcome! Please ensure:
1. All tests pass: `pytest`
2. Code follows the project style
3. New features include tests
4. Documentation is updated

## License

See LICENSE file for details.

## Support

For issues, questions, or contributions, please visit the [GitHub repository](https://github.com/s-andrews/lipidmaps_py).
