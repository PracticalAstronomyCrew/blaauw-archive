from __future__ import annotations

import argparse
import pickle
import socket
from sys import argv

import logging as log

from pathlib import Path
from typing import List, Optional
from astropy.time import Time
from sqlalchemy import create_engine, select, text, update
from sqlalchemy.orm import Session
from blaauw.core import models, transformers

RUNNING_SERVER = False

def create_observation(header: dict) -> models.Observation:
    """
    Given a header, creates an Observation out of it.
    """
    # Assume utc
    date_str = header["DATE-OBS"]
    # maybe format="isot" ?
    date = Time(date_str, format="fits", scale="utc")

    imtyp = header.get("IMAGETYP", None)
    filter = header.get("FILTER", None)
    obj = header.get("OBJECT", None)
    xbin = header["XBINNING"]
    ybin = header["YBINNING"]
    binning = xbin if xbin == ybin else None
    filename = Path(header["FILENAME"])
    telescope = models.Telescope.from_path(filename)
    file_id = transformers.path_to_file_id(filename)

    ra, dec = transformers.get_equitorial(header)
    alt, az = transformers.get_horizontal(header)
    # Maybe: if alt-az not available, but ra & dec are. Calculate them ?
    # Same for airmass

    exposure_time = header.get("EXPTIME", None)
    if exposure_time is None:
        exposure_time = header.get("EXPOSURE", None)

    obs = models.Observation(
            filename=header["FILENAME"],
            file_id=file_id,
            date_obs = date.to_datetime(),
            date_obs_mjd = date.mjd,

            ra = ra,
            dec = dec,
            alt = alt,
            az = az,
            airmass = header.get("AIRMASS", None),

            image_type = transformers.imtyp_to_enum(imtyp, filter=filter, obj=obj),
            filter = filter,
            target_object = obj,
            exposure_time = exposure_time,
            binning = binning,

            telescope = telescope,
            instrument = header.get("INSTRUME", None),
    )
    return obs

def checked_add(observation: models.Observation, session: Session) -> Optional[models.Observation]:
    """
    If the observation (file_id) is not in the database, will add it to the session and
    return None. When it is already in there, will not add it but return it to
    be updated.
    """
    select_stmt = select(models.Observation).where(models.Observation.file_id == observation.file_id)
    exists = session.scalars(select_stmt).first()
    if exists is not None:
        return observation

    session.add(observation)
    return None
    

def insert_header_list(headers: List[dict], engine):
        data = headers

        # Create all the observation objects
        observations = []
        for header in data:
            obs = create_observation(header)
            observations.append(obs)

        log.info(f"--------------------------------------------------------------------------------")
        log.info(f"- Inserting {len(observations)} observations (if not existing) ...")
        log.info(f"--------------------------------------------------------------------------------")
        # Insert everything
        to_update: List[models.Observation] = []
        with Session(engine) as session:
            for obs in observations:
                obs_update = checked_add(obs, session)
                if obs_update is not None:
                    to_update.append(obs_update)
            session.commit()
    
        log.info(f"--------------------------------------------------------------------------------")
        log.info(f"- {len(observations) - len(to_update)} inserted, now updating {len(to_update)} elements...")
        log.info(f"--------------------------------------------------------------------------------")

        update_stmt = update(models.Observation)
        update_params = set(update_stmt.compile().params) - {'id', 'created_at', 'updated_at'}
        with Session(engine) as session:
            for obs in to_update:
                obs_update = update_stmt.where(models.Observation.file_id == obs.file_id).values({k: getattr(obs, k) for k in update_params}) 
                session.execute(obs_update)
            session.commit()

        log.info(f"--------------------------------------------------------------------------------")
        log.info(f"- Done updating")
        log.info(f"--------------------------------------------------------------------------------")

def main(args: argparse.Namespace):
    # TODO: Make this more general for any hostname, password etc.
    log.info(f"Starting run (server={RUNNING_SERVER})")
    log.info("Connecting to database")
    if RUNNING_SERVER:
        engine = create_engine("postgresql+psycopg2:///dachs", echo=args.echo)
    else:
        # Local version
        engine = create_engine("postgresql+psycopg2://postgres:password@localhost:5432/dachs", echo=args.echo)

    if args.reload_db:
        log.info("Recreating database from scratch")
        with Session(engine) as session:
            log.info("Dropping schema")
            session.execute(text("drop schema if exists blaauw cascade"))
            session.commit()

        with Session(engine) as session:
            log.info("Dropping recreating schema")
            session.execute(text("create schema blaauw"))
            session.commit()
        # We need to make sure here that we grant privileges to the relevant tables (see below for example)

        # dachs=# GRANT ALL PRIVILEGES ON SCHEMA blaauw TO feed WITH GRANT OPTION;
        # dachs=# GRANT SELECT ON blaauw.raw TO feed WITH GRANT OPTION;

        # GRANT ALL PRIVILEGES ON SCHEMA observations TO feed WITH GRANT OPTION;
        # GRANT SELECT ON observations.raw TO feed WITH GRANT OPTION;
        # GRANT SELECT ON observations.reduced TO feed WITH GRANT OPTION;
        # GRANT SELECT ON observations.calibration TO feed WITH GRANT OPTION;
        # GRANT SELECT ON observations.composition TO feed WITH GRANT OPTION;

    models.Base.metadata.create_all(engine) # Init

    # If running on the server, grant privileges to all the tables
    if args.reload_db and RUNNING_SERVER:
        with Session(engine) as session:
            session.execute(text("GRANT ALL PRIVILEGES ON SCHEMA blaauw TO feed WITH GRANT OPTION"))
            for table in models.Base.metadata.tables.keys():
                session.execute(text(f"GRANT SELECT ON {table} TO feed WITH GRANT OPTION"))
            session.commit()

    # if args.reload_db:
    #     header_files = ["../data/latest-headers.txt", "../data/processed-headers.txt"]
    #     for header_file in header_files:
    #         with open(header_file, "rb") as f:
    #             data = pickle.load(f)
    #         log.info(f"---------------------------------------------------------------------------------------")
    #         log.info(f"- Creating observations from {header_file}")
    #         log.info(f"---------------------------------------------------------------------------------------")
    #         insert_header_list(data, engine)

    if args.file:
        with open(args.file, "rb") as f:
            data = pickle.load(f)
        log.info(f"--------------------------------------------------------------------------------")
        log.info(f"- Creating observations from {args.file}")
        log.info(f"--------------------------------------------------------------------------------")
        insert_header_list(data, engine)

    # Report what is in there
    with Session(engine) as session:
        sl = select(models.Observation)
        all_obs = len(session.scalars(sl).all())
        sl_first = select(models.Observation).add_columns(models.Observation.date_obs).order_by(models.Observation.date_obs.asc())
        sl_last = select(models.Observation).add_columns(models.Observation.date_obs).order_by(models.Observation.date_obs.desc())
        first = session.scalars(sl_first).first()
        last = session.scalars(sl_last).first()

    log.info(f"--------------------------------------------------------------------------------")
    log.info(f"- We have {all_obs} entries")
    if first is not None and last is not None:
        log.info(f"- Ranging from {first.date_obs.date()} to {last.date_obs.date()}")
    log.info(f"--------------------------------------------------------------------------------")

def parse() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", type=str)
    parser.add_argument("--reload-db", action="store_true")
    parser.add_argument("--echo", action="store_true")
    parser.add_argument("--debug", action="store_true")
    return parser.parse_args()

if __name__ == '__main__':

    args = parse()
    if args.debug:
        log.basicConfig(level=log.DEBUG)
    else:
        log.basicConfig(level=log.INFO)
    RUNNING_SERVER = socket.gethostname() == "voserver.astro.rug.nl"
    main(args)
