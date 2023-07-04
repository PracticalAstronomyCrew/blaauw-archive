from datetime import datetime
import enum
from pathlib import Path
from typing import Optional
from sqlalchemy import Enum, UniqueConstraint, func
from sqlalchemy.types import DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    __table_args__ = {"schema": "blaauw"}
    pass

class ImageType(enum.Enum):
    BIAS = "Bias"
    DARK = "Dark"
    FLAT = "Flat"
    LIGHT = "Light"


RAW_GBT = Path("/net/vega/data/users/observatory/images/")
RAW_LDST = Path("/net/vega/data/users/observatory/LDST")
ASTROM_GBT = Path("/net/dataserver3/data/users/noelstorr/blaauwastrom/")
PIPE_GBT = Path("/net/dataserver3/data/users/noelstorr/blaauwpipe/")

# GBT:
# SITELAT  '+53:14:24.90',
# SITELONG '-006:32:11.20',

class Telescope(enum.Enum):
    LDST = "LDST" #Lauwersmeer Dark Sky Telescope
    GBT = "GBT" #Gratema Bernoulli Telescope

    @classmethod
    def from_path(cls, path: Path):
        parents = path.parents
        if RAW_GBT in parents or ASTROM_GBT in parents:
            return cls.GBT
        if RAW_LDST in parents:
            return cls.LDST
        return None

    def __str__(self) -> str:
        return self.name


class Observation(Base):
    __tablename__ = "raw"

    id: Mapped[int] = mapped_column(primary_key=True)
    filename: Mapped[str]
    file_id: Mapped[str]
    date: Mapped[datetime]
    date_mjd: Mapped[float]

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
    created_at: Mapped[datetime] = mapped_column(insert_default=func.CURRENT_TIMESTAMP())
    updated_at: Mapped[datetime] = mapped_column(insert_default=func.CURRENT_TIMESTAMP(), onupdate=func.now())


    def __repr__(self) -> str:
        return f"Observation(filename={self.filename.split('/')[-1]}, date='{self.date}', object={self.target_object}, image_type={self.image_type}, filter={self.filter}, telescope={self.telescope}, created_at='{self.created_at}', updated_at='{self.updated_at}')"
