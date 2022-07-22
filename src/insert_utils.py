import logging as log
from collections import defaultdict

from postgres import Postgres
from psycopg2.errors import UniqueViolation

from queries import make_insert_query, make_update_query

"""
We have:
    - raw files
    - calibration files
    - reduced files

1. Insert / update raw files.
2. Insert / update calibrated files
3. Link calibrated files with raw files
4. Insert / update reduced files
"""


def insert_raw(headers: list[dict], columns: list[dict], db: Postgres):
    unprocessed = []

    query = make_insert_query(columns, table_name="raw")

    log.info(f"Inserting {len(headers)} new headers...")
    for header in headers:
        with db.get_cursor() as curs:
            # Make the statement
            try:
                curs.run(query, parameters=defaultdict(lambda: None, header))
            except UniqueViolation as e:
                # Handle the failed connection error as well
                log.info(
                    "UniqueViolation. Header probably already in the database. "
                    f"Updating header of {header['FILENAME']} later"
                )
                unprocessed.append(header)
    log.info(f"Done: Inserted {len(headers) - len(unprocessed)} new items.")

    log.info(f"Updating {len(unprocessed)} headers...")
    exceptions = 0
    for header in unprocessed:
        # Depends on what is in the header
        query = make_update_query(header, columns, table_name="raw")
        with db.get_cursor() as curs:
            try:
                curs.run(query, parameters=header)
            except Exception as e:
                log.exception(
                    f"Exception in updating, {e}. "
                    f"Happened with file {header['FILENAME']}"
                )
                exceptions += 1
    log.info(f"Done: Updated {len(unprocessed) - exceptions} items.")

    return exceptions
