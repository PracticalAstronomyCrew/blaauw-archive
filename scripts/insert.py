from __future__ import annotations

import argparse
import enum
import logging as log
import pickle
import socket
from pathlib import Path
from typing import List, Optional

from astropy.coordinates import AltAz, SkyCoord
from astropy.time import Time
from sqlalchemy import create_engine, select, text, update
from sqlalchemy.orm import Session
from tqdm import tqdm

from blaauw.core import models, transformers

RUNNING_SERVER = False


def create_observation_from_header(header: dict) -> models.Observation:
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

    airmass = header.get("AIRMASS", None)
    ra, dec = transformers.get_equitorial(header)
    # if ra & dec are available calculate alt az and airmass.
    # TODO: probably only do this if astrometry is available (most reliable)
    if dec is not None and ra is not None and telescope is not None:
        coord = SkyCoord(ra, dec, obstime=date, unit="deg")
        horizontal_frame = coord.transform_to(AltAz(location=telescope.location()))

        alt = horizontal_frame.alt.deg
        az = horizontal_frame.az.deg
        airmass = horizontal_frame.secz.value
    else:
        alt, az = transformers.get_horizontal(header)

    exposure_time = header.get("EXPTIME", None)
    if exposure_time is None:
        exposure_time = header.get("EXPOSURE", None)

    image_type = transformers.imtyp_to_enum(imtyp, filter=filter, obj=obj)

    obs = models.Observation(
        filename=str(filename),
        date_obs=date.to_datetime(),
        date_obs_mjd=date.mjd,
        ra=ra,
        dec=dec,
        alt=alt,
        az=az,
        airmass=airmass,
        image_type=image_type,
        filter=filter,
        target_object=obj,
        exposure_time=exposure_time,
        binning=binning,
        telescope=telescope,
        instrument=header.get("INSTRUME", None),
    )
    return obs


# def checked_add(
#     observation: models.Observation, session: Session
# ) -> Optional[models.Observation]:
#     """
#     If the observation (filename) is not in the database, will add it to the
#     session and return None. When it is already in there, will not add it but
#     return it to be updated.
#     """
#     select_stmt = select(models.Observation).where(
#         models.Observation.filename == observation.filename
#     )
#     exists = session.scalars(select_stmt).first()
#     if exists is not None:
#         return observation
#
#     session.add(observation)
#     return None


# Create a reusable update statement, and determine which parameters to update
_update_stmt = update(models.Observation)
_update_params = set(_update_stmt.compile().params) - {
    "id",
    "created_at",
    "updated_at",
}


class DBOperationEnum(enum.Enum):
    INSERTED = "inserted"
    UPDATED = "updated"


def insert_observation(
    observation: models.Observation, session: Session
) -> DBOperationEnum:
    """
    Will insert the given `observation` in the databse (via the `session`). There will
    be two cases:
        - The observation (filename) is not in the database yet: it will be added.
        - The observation is already in the database: it will be updated with the
    """
    select_stmt = select(models.Observation).where(
        models.Observation.filename == observation.filename
    )
    existing_obs = session.scalars(select_stmt).first()
    if existing_obs is None:
        session.add(observation)
        return DBOperationEnum.INSERTED

    obs_update = _update_stmt.where(
        models.Observation.filename == observation.filename
    ).values({k: getattr(observation, k) for k in _update_params})
    session.execute(obs_update)
    return DBOperationEnum.UPDATED


def insert_header_list(headers: List[dict], engine):
    """
    Given a list of headers, will create Observation objects and insert them into the
    database.

    It will print some statistics on the number of inserted/updated observations.
    """
    # Create all the observation objects
    observations = []
    for header in headers:
        obs = create_observation_from_header(header)
        observations.append(obs)

    log.info(
        "--------------------------------------------------------------------------------"
    )
    log.info(f"- Inserting {len(observations)} observations...")
    log.info(
        "--------------------------------------------------------------------------------"
    )
    # Insert everything
    num_inserted = 0
    with Session(engine) as session:
        if args.progress_bar:
            iterator = tqdm(observations)
        else:
            iterator = observations

        for obs in iterator:
            operation_done = insert_observation(obs, session)
            if operation_done == DBOperationEnum.INSERTED:
                num_inserted += 1
        session.commit()

    log.info(
        "--------------------------------------------------------------------------------"
    )
    log.info(f"- Inserted {num_inserted}, Updated {len(observations) - num_inserted}")
    log.info("- Done")
    log.info(
        "--------------------------------------------------------------------------------"
    )


def main(args: argparse.Namespace):
    # TODO: Make this more general for any hostname, password etc.
    log.info(f"Starting run (server={RUNNING_SERVER})")
    log.info("Connecting to database")
    if RUNNING_SERVER:
        engine = create_engine("postgresql+psycopg2:///dachs", echo=args.echo)
    else:
        # Local version
        engine = create_engine(
            "postgresql+psycopg2://postgres:password@localhost:5432/dachs",
            echo=args.echo,
        )

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

    models.Base.metadata.create_all(engine)  # Init

    # If running on the server, grant privileges to all the tables
    # We need to make sure here that we grant privileges to the relevant
    # tables (see below for example)

    # dachs=# GRANT ALL PRIVILEGES ON SCHEMA blaauw TO feed WITH GRANT OPTION;
    # dachs=# GRANT SELECT ON blaauw.raw TO feed WITH GRANT OPTION;
    # The last needs to be executed for all tables
    if args.reload_db and RUNNING_SERVER:
        with Session(engine) as session:
            session.execute(
                text("GRANT ALL PRIVILEGES ON SCHEMA blaauw TO feed WITH GRANT OPTION")
            )
            for table in models.Base.metadata.tables.keys():
                session.execute(
                    text(f"GRANT SELECT ON {table} TO feed WITH GRANT OPTION")
                )
            session.commit()

    if args.file:
        with open(args.file, "rb") as f:
            data = pickle.load(f)
        log.info(
            "--------------------------------------------------------------------------------"
        )
        log.info(f"- Creating observations from {args.file}")
        log.info(
            "--------------------------------------------------------------------------------"
        )
        insert_header_list(data, engine)

    # Report what is in there
    with Session(engine) as session:
        sl = select(models.Observation)
        all_obs = len(session.scalars(sl).all())
        sl_first = (
            select(models.Observation)
            .add_columns(models.Observation.date_obs)
            .order_by(models.Observation.date_obs.asc())
        )
        sl_last = (
            select(models.Observation)
            .add_columns(models.Observation.date_obs)
            .order_by(models.Observation.date_obs.desc())
        )
        first = session.scalars(sl_first).first()
        last = session.scalars(sl_last).first()

    log.info(
        "--------------------------------------------------------------------------------"
    )
    log.info(f"- We have {all_obs} entries")
    if first is not None and last is not None:
        log.info(f"- Ranging from {first.date_obs.date()} to {last.date_obs.date()}")
    log.info(
        "--------------------------------------------------------------------------------"
    )


def parse() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", type=str)
    parser.add_argument("--reload-db", action="store_true")
    parser.add_argument("--echo", action="store_true")
    parser.add_argument("--debug", action="store_true")
    parser.add_argument("--progress-bar", action="store_true")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse()
    if args.debug:
        log.basicConfig(level=log.DEBUG)
    else:
        log.basicConfig(level=log.INFO)

    RUNNING_SERVER = socket.gethostname() == "voserver.vm.astro.rug.nl"
    main(args)
