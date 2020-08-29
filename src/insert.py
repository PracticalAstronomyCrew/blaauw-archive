import sys

from pickle import load
from pprint import pprint
from collections import defaultdict

from astropy.time import Time
from astropy.coordinates import SkyCoord
from astropy import units as u

from postgres import Postgres, UniqueViolation
from columns import read_columns
import csv

# Set of all the dictionary keys, which are entries in the database.
# TODO read from the .csv file
# DB_HEADERS = {
#    "SIMPLE",
#    "BITPIX",
#    "NAXIS",
#    "NAXIS1",
#    "NAXIS2",
#    "BSCALE",
#    "BZERO",
#    "BIAS",
#    "FOCALLEN",
#    "APTAREA",
#    "APTDIA",
#    "DATE-OBS",
#    "TIME-OBS",
#    "SWCREATE",
#    "SET-TEMP",
#    "COLORCCD",
#    "DISPCOLR",
#    "IMAGETYP",
#    "CCDSFPT",
#    "XORGSUBF",
#    "YORGSUBF",
#    "CCDSUBFL",
#    "CCDSUBFT",
#    "XBINNING",
#    "CCDXBIN",
#    "YBINNING",
#    "CCDYBIN",
#    "EXPSTATE",
#    "CCD-TEMP",
#    "TEMPERAT",
#    "OBJECT",
#    "OBJCTRA",
#    "OBJCTDEC",
#    "TELTKRA",
#    "TELTKDEC",
#    "CENTAZ",
#    "CENTALT",
#    "TELHA",
#    "LST",
#    "AIRMASS",
#    "SITELAT",
#    "SITELONG",
#    "INSTRUME",
#    "EGAIN",
#    "E-GAIN",
#    "XPIXSZ",
#    "YPIXSZ",
#    "SBIGIMG",
#    "USER_2",
#    "DATAMAX",
#    "SBSTDVER",
#    "FILTER",
#    "EXPTIME",
#    "EXPOSURE",
#    "CBLACK",
#    "CWHITE",
#    "FILENAME",
#    "obs_jd",
#    "ra",
#    "dec",
#    "CTYPE1",
#    "CTYPE2",
#    "EQUINOX",
#    "CRVAL1",
#    "CRVAL2",
#    "CRPIX1",
#    "CRPIX2",
#    "CUNIT1",
#    "CUNIT2",
#    "CD1_1",
#    "CD1_2",
#    "CD2_1",
#    "CD2_2",
#    "PLATE_SCALE",
# }


def prep_sql_statement(columns):
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
        add_jd(head)
        add_pos(head)
        # TODO: process PLATE_SCALE here, not in the crawler

    # check if any of the keys in the dict are not used in the database
    used_headers = set(col["py-name"] for col in columns)
    for head in headers:
        unused = head.keys() - used_headers
        if len(unused):
            name_str = ". File: " + head.get("FILENAME", "")
            print(f"[Warning] - Unused FITS headers{name_str} {unused}")

    sql_stmt = prep_sql_statement(columns)

    if CONNECT_DB:
        db_url = "dbname=gavo"
        db = Postgres(db_url)

        with db.get_cursor() as curs:
            for header in headers:
                # convert the header to a defaultdict which gives None if the
                # key is not present.
                try:
                    curs.run(
                        sql_stmt, parameters=defaultdict(lambda: None, header)
                    )
                except UniqueViolation as e:
                    print("UniqueViolation:", e)
                    print("Header probably already in the database.")
                    print(
                        f'skipping header {header.get("FILENAME", "NA")} ...'
                    )
                    # TODO: Add an update query here


def add_jd(head: dict):
    """
    add_jd creates a new item 'obs_jd' in head containing the Observation Date
    in Julian Days.  'obs_jd' is derived from 'DATE-OBS' and only adds it if
    that entry exists
    """
    if "DATE-OBS" in head:
        time = Time(head["DATE-OBS"], format="isot", scale="utc")
        head["obs_jd"] = time.jd


def add_pos(head: dict):
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
