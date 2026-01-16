"""
LIPID MAPS Python API
=====================

A Python package for importing, processing, and analyzing lipid data
using LIPID MAPS resources.

Main functions:
    - import_data: Import lipid data from CSV files
    - import_msdial: Import MS-DIAL formatted data

Main classes:
    - LipidData: High-level interface for imported lipid data

Subpackages:
    - data: Data input framework for pathway analysis
    - tools: Utility tools and helpers
"""

# Convenience wrapper for direct CSV processing
from .data.data_manager import DataManager


def process_csv(csv_path, **kwargs):
    """
    Directly process a CSV file into a LipidDataset using DataManager.
    Accepts all DataManager keyword arguments.
    Example:
        from lipidmaps import process_csv
        dataset = process_csv("your_file.csv", validate_data=True)
    """
    manager = DataManager(**kwargs)
    return manager.process_csv(csv_path)

from .data_importer import import_data, import_msdial, LipidData

# Import subpackages to make them accessible
from . import data

__version__ = "0.1.0"
__all__ = ["import_data", "import_msdial", "LipidData", "data"]
