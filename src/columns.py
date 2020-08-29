import csv


def read_columns(filename):
    with open(filename, "r") as f:
        columns_reader = csv.DictReader(f)
        columns_dicts = [d for d in columns_reader]
    return columns_dicts
