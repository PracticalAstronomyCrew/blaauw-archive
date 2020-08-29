import csv


def read_columns(filename):
    with open(filename, "r") as f:
        columns_dict = csv.DictReader(f)
    return columns_dict
