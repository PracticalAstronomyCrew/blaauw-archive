import sys
import csv
import os

from pickle import load
from pprint import pprint
from collections import defaultdict

from astropy.time import Time
from astropy.coordinates import SkyCoord
from astropy import units as u

from postgres import Postgres
from psycopg2.errors import UniqueViolation

from columns import read_columns
from table_sql import type_map

# table name, colname, type
add_col_fmt = "ALTER TABLE {} ADD COLUMN {} {};"
csv_fmt = "{0},{0},{1},,,"
# header, py header, type, ....


def make_update_statement(header: dict, columns: list) -> str:
    keys = (col for col in columns if col["py-name"] in header)
    set_data = ", ".join(
        f"{col['name']} = %({col['py-name']})s" for col in keys
    )

    update_stmt = "UPDATE observations.raw SET {} WHERE file_id = %(file_id)s"
    return update_stmt.format(set_data)


def prep_sql_statement(columns: list) -> str:
    # make the sql insert statement
    colnames = ", ".join(col["name"] for col in columns)
    colnames = "(" + colnames + ")"

    insnames = ", ".join(f"%({col['py-name']})s" for col in columns)
    insnames = "(" + insnames + ")"

    insert_stmt = (
        "INSERT INTO observations.raw " + colnames + " VALUES " + insnames
    )
    return insert_stmt


# Toggle to turn on/off
CONNECT_DB = True


def main(filename: str, col_files: str):

    print("Running on file: {}".format(filename))

    # read headers from pickled file
    with open(filename, "rb") as f:
        headers = load(f)

    # read columns from csv file
    with open(col_files, "r") as f:
        columns = read_columns(col_files)

    # calculate JD
    # calculate RA DEC
    for head in headers:
        add_file_id(head)
        add_jd(head)
        add_pos(head)

    # check if any of the keys in the dict are not used in the database
    used_headers = set(col["py-name"] for col in columns)
    new_headers = set()
    update_later = []
    for head in headers:
        unused = head.keys() - used_headers
        if len(unused):
            name_str = ". File: " + head.get("FILENAME", "")
            print(f"[Warning] - Unused FITS headers{name_str} {unused}")
            # TODO: add new column;
            # https://www.postgresql.org/docs/13/sql-altertable.html
        new_headers |= {(key, type(head[key])) for key in unused}
        update_later.append(head)
        
    # TODO: add check verifying no duplicate keys are in here
    # TODO: update the column_list.csv file with the new headers
    # TODO: trigger update for DaCHS (or maybe next step in the CRON job)
    print("New Headers Found: ", new_headers)
    print("--- start column statements ---")
    for key, typ in new_headers:
        print(add_col_fmt.format("observations.raw", key, type_map[typ.__name__]))
    print("---- end column statements ----")
    print("")
    print("--- start csv statements ---")
    for key, typ in new_headers:
        print(csv_fmt.format(key, typ.__name__))
    print("---- end csv statements ----")

    sql_stmt = prep_sql_statement(columns)

    if CONNECT_DB:
        db_url = "dbname=dachs"
        db = Postgres(db_url)
        uprocessed = []

        print("Inserting new headers")
        for header in headers:
            # Insert new headers if not yet in the database
            with db.get_cursor() as curs:
                # convert the header to a defaultdict which gives None if the
                # key is not present.
                try:
                    curs.run(
                        sql_stmt, parameters=defaultdict(lambda: None, header)
                    )
                except UniqueViolation as e:
                    # Handle the failed connection error as well
                    print(
                        "UniqueViolation. Header probably already in the database."
                    )
                    print(f"Updating header of {header['FILENAME']} later")
                    uprocessed.append(header)

        print("Updating already existing headers")
        for header in uprocessed:
            # Update already existing headers
            with db.get_cursor() as curs:
                update_stmt = make_update_statement(header, columns)
                try:
                    curs.run(update_stmt, parameters=header)
                except Exception as e:
                    print("Exception in updating,", e)
                    print("Happened with header of file:", header["FILENAME"])


def add_file_id(head: dict) -> None:
    """
    Add the header 'file_id' to the header, which is the combination of date
    and filename (without full path). It is used to compare processed and
    uprocessed files, to ensure there are no duplicates in there.
    """
    if "FILENAME" in head:
        fn = head["FILENAME"]
        splitted = fn.split("/")
        if "blaauwastrom" in fn:
            head["file_id"] = splitted[7] + "/" + splitted[8]
        else:
            head["file_id"] = splitted[7] + "/" + splitted[10]


def add_jd(head: dict) -> None:
    """
    add_jd creates a new item 'obs_jd' in head containing the Observation Date
    in Julian Days.  'obs_jd' is derived from 'DATE-OBS' and only adds it if
    that entry exists
    """
    if "DATE-OBS" in head:
        time = Time(head["DATE-OBS"], format="isot", scale="utc")
        head["obs_jd"] = time.jd


def add_pos(head: dict) -> None:
    """
    add_pos creates two new entries 'ra' and 'dec' which are degree versions of
    the 'OBJCTRA' and 'OBJCTDEC' entries. Only creates the now entries of these
    exist.
    """
    if "CRVAL1" in head and "CRVAL2" in head:
        head["ra"], head["dec"] = head["CRVAL1"], head["CRVAL2"]
    elif "OBJCTRA" in head and "OBJCTDEC" in head:
        coord = SkyCoord(
            head["OBJCTRA"], head["OBJCTDEC"], unit=(u.hourangle, u.deg)
        )
        head["ra"], head["dec"] = coord.ra.degree, coord.dec.degree


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage:")
        print("$ python3 insert.py [file to insert] [column csv file]")
        exit(-1)
    main(*sys.argv[1:])
