import enum
from datetime import datetime
from pathlib import Path
from typing import Optional

from astropy.coordinates import EarthLocation, Latitude, Longitude
from sqlalchemy import func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class ImageType(enum.Enum):
    BIAS = "Bias"
    DARK = "Dark"
    FLAT = "Flat"
    LIGHT = "Light"


RAW_GBT = Path("/net/vega/data/users/observatory/images/")
RAW_LDST = Path("/net/vega/data/users/observatory/LDST")
ASTROM_GBT = Path("/net/dataserver3/data/users/noelstorr/blaauwastrom/")
PIPE_GBT = Path("/net/dataserver3/data/users/noelstorr/blaauwpipe/")

BASE_DIR_MAP = {
    "RAW_GBT": RAW_GBT,
    "RAW_LDST": RAW_LDST,
    "ASTROM_GBT": ASTROM_GBT,
    "PIPE_GBT": PIPE_GBT,
}

GBT_LOCATION = EarthLocation.from_geodetic(
    lon=Longitude("06d32m11.20s"), lat=Latitude("+53d14m24.90s"), height=0
)
LDST_LOCATION = EarthLocation.from_geodetic(
    lon=Longitude("06d14m05s"), lat=Latitude("+53d23m04s"), height=0
)


class Telescope(enum.Enum):
    LDST = "LDST"  # Lauwersmeer Dark Sky Telescope
    GBT = "GBT"  # Gratema Bernoulli Telescope

    @classmethod
    def from_path(cls, path: Path):
        parents = path.parents
        if RAW_GBT in parents or ASTROM_GBT in parents:
            return cls.GBT
        if RAW_LDST in parents:
            return cls.LDST
        return None

    def location(self) -> EarthLocation:
        if self is Telescope.LDST:
            return LDST_LOCATION
        else:
            return GBT_LOCATION

    def __str__(self) -> str:
        return self.name


class Base(DeclarativeBase):
    __table_args__ = {"schema": "blaauw"}
    pass


class Observation(Base):
    __tablename__ = "raw"
    id: Mapped[int] = mapped_column(primary_key=True)
    filename: Mapped[str] = mapped_column(unique=True)
    file_id: Mapped[str] = mapped_column(unique=True)
    date_obs: Mapped[datetime]
    date_obs_mjd: Mapped[float]

    ra: Mapped[Optional[float]]
    dec: Mapped[Optional[float]]
    alt: Mapped[Optional[float]]
    az: Mapped[Optional[float]]
    airmass: Mapped[Optional[float]]

    # Obs info
    image_type: Mapped[Optional[ImageType]]
    filter: Mapped[Optional[str]]
    target_object: Mapped[Optional[str]]
    exposure_time: Mapped[float]
    binning: Mapped[Optional[int]]

    # instrument meta data
    telescope: Mapped[Telescope]
    instrument: Mapped[Optional[str]]

    # db metadata (automatic)
    created_at: Mapped[datetime] = mapped_column(
        insert_default=func.CURRENT_TIMESTAMP()
    )
    updated_at: Mapped[datetime] = mapped_column(
        insert_default=func.CURRENT_TIMESTAMP(), onupdate=func.now()
    )

    def __repr__(self) -> str:
        return f"Observation(file_id={self.file_id}, date_obs='{self.date_obs}', image_type={self.image_type}, filter={self.filter}, telescope={self.telescope}, filename={self.filename.split('/')[-1]}, created_at='{self.created_at}', updated_at='{self.updated_at}')"
