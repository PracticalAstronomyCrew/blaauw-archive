import argparse
import pickle
from sys import argv

import logging as log

from pathlib import Path
from typing import List, Optional
from astropy.time import Time
from sqlalchemy import create_engine, select, text, update
from sqlalchemy.orm import Session
from blaauw.core import models, transformers


def create_observation(header: dict):
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
            date = date.to_datetime(),
            date_mjd = date.mjd,

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

        log.info(f"---------------------------------------------------------------------------------------")
        log.info(f"- Inserting {len(observations)} observations (if not existing) ...")
        log.info(f"---------------------------------------------------------------------------------------")
        # Insert everything
        to_update: List[models.Observation] = []
        with Session(engine) as session:
            for obs in observations:
                obs_update = checked_add(obs, session)
                if obs_update is not None:
                    to_update.append(obs_update)
            session.commit()
    
        log.info(f"---------------------------------------------------------------------------------------")
        log.info(f"- {len(observations) - len(to_update)} inserted, now updating {len(to_update)} elements...")
        log.info(f"---------------------------------------------------------------------------------------")

        update_stmt = update(models.Observation)
        update_params = set(update_stmt.compile().params) - {'id', 'created_at', 'updated_at'}
        with Session(engine) as session:
            for obs in to_update:
                obs_update = update_stmt.where(models.Observation.file_id == obs.file_id).values({k: getattr(obs, k) for k in update_params}) 
                session.execute(obs_update)
            session.commit()

        log.info(f"---------------------------------------------------------------------------------------")
        log.info(f"- Done updating")
        log.info(f"---------------------------------------------------------------------------------------")

def main(args: argparse.Namespace):
    # Init database (from scratch)
    engine = create_engine("postgresql+psycopg2://postgres:password@localhost:5432/dachs", echo=args.echo)

    if args.reload_db:
        with Session(engine) as session:
            session.execute(text("drop schema if exists blaauw cascade"))
            session.commit()

        with Session(engine) as session:
            session.execute(text("create schema blaauw"))
            session.commit()

    models.Base.metadata.create_all(engine) # Init

    if args.reload_db:
        header_files = ["./data/latest-headers.txt", "./data/processed-headers.txt"]
        for header_file in header_files:
            with open(header_file, "rb") as f:
                data = pickle.load(f)
            log.info(f"---------------------------------------------------------------------------------------")
            log.info(f"- Creating observations from {header_file}")
            log.info(f"---------------------------------------------------------------------------------------")
            insert_header_list(data, engine)

    # Can it be empty?
    if args.file:
        with open(args.file, "rb") as f:
            data = pickle.load(f)
        log.info(f"---------------------------------------------------------------------------------------")
        log.info(f"- Creating observations from {args.file}")
        log.info(f"---------------------------------------------------------------------------------------")
        insert_header_list(data, engine)

    # Report what is in there
    with Session(engine) as session:
        sl = select(models.Observation)
        all_obs = len(session.scalars(sl).all())
        if all_obs > 0:
            sl_first = select(models.Observation).add_columns(models.Observation.date).order_by(models.Observation.date.asc())
            sl_last = select(models.Observation).add_columns(models.Observation.date).order_by(models.Observation.date.desc())
            first = session.scalars(sl_first).first()
            last = session.scalars(sl_last).first()

    log.info(f"---------------------------------------------------------------------------------------")
    log.info(f"- We have {all_obs} entries")
    if all_obs > 0:
        log.info(f"- Ranging from {first.date.date()} to {last.date.date()}")
    log.info(f"---------------------------------------------------------------------------------------")

def parse() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", type=str)
    # parser.add_argument("--raw", type=str)
    # parser.add_argument("--use-db", action="store_true")
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
    main(args)

