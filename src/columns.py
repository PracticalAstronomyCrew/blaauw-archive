import csv
from typing import List, Dict


def read_columns(filename: str) -> List[Dict[str, str]]:
    with open(filename, "r") as f:
        columns_reader = csv.DictReader(f)
        columns_dicts = [d for d in columns_reader]
    return columns_dicts


def combine_tables(filenames: List[str]) -> List[Dict[str, str]]:
    combined = []
    for fn in filenames:
        combined.extend(read_columns(fn))
    return combined
