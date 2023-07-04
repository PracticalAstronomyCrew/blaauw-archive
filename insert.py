import pickle
from sys import argv

from pathlib import Path
from astropy.time import Time
from sqlalchemy import create_engine, select, text
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

def main():
    # Init database (from scratch)
    engine = create_engine("postgresql+psycopg2://postgres:password@localhost:5432/dachs", echo=True)
    models.Base.metadata.create_all(engine) # Init

    if "reload" in argv:
        with Session(engine) as session:
            session.query(text("drop schema blaauw cascade"))

        models.Base.metadata.drop_all(engine)   # Clear
        models.Base.metadata.create_all(engine) # Init

        header_file = "./data/latest-headers.txt"
        with open(header_file, "rb") as f:
            data = pickle.load(f)

        # Insert everything
        with Session(engine) as session:
            observations = []
            for header in data:
                obs = create_observation(header)
                observations.append(obs)

            session.add_all(observations)
            session.commit()

    with Session(engine) as session:
        sl = select(models.Observation)
        all_obs = len(session.scalars(sl).all())
        if all_obs > 0:
            sl_first = select(models.Observation).column(models.Observation.date).order_by(models.Observation.date.asc())
            sl_last = select(models.Observation).column(models.Observation.date).order_by(models.Observation.date.desc())
            first = session.scalars(sl_first).first()
            last = session.scalars(sl_last).first()

    print(f"---------------------------------------------------------------------------------------")
    print(f"- We have {all_obs} entries")
    if all_obs > 0:
        print(f"- Ranging from {first.date.date()} to {last.date.date()}")
    print(f"---------------------------------------------------------------------------------------")

    # Do again!
    # with Session(engine) as session:
    #     for header in data[-25:-15]:
    #         obs = create_observation(header)
    #         exists_stmt = select(models.Observation).where(models.Observation.date_mjd == obs.date_mjd and models.Observation.telescope == obs.telescope).exists()
    #         exists = session.query(exists_stmt)
    #         if not exists:
    #             session.add(obs)
    #
    #     session.commit()

if __name__ == '__main__':
    main()

