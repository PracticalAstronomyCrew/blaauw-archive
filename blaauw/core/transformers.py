from typing import Optional
from blaauw.core import models
from pathlib import Path

from astropy.coordinates import SkyCoord
import astropy.units as u


def imtyp_to_enum(imtyp: Optional[str] = None, filter: Optional[str] = None, obj: Optional[str] = None) -> Optional[models.ImageType]:
    """
    Attempts to derive the image type from the values in the header. The easiest case
    is when IMAGETYP is correctly set, but otherwise try to get it from information
    in the FILTER or OBJECT keyword.
    """
    if imtyp is not None:
        if imtyp.lower() in ("bias", "bias frame"):
            return models.ImageType.BIAS
        if imtyp.lower() in ("flat", "flat field"):
            return models.ImageType.FLAT
        if imtyp.lower() in ("dark", "dark frame"):
            return models.ImageType.DARK
        if imtyp.lower() in ("light", "light frame"):
            return models.ImageType.LIGHT

    if filter is not None:
        if filter.lower() == "dark":
            return models.ImageType.DARK

    if obj is not None:
        obj_cmp = obj.lower().strip()
        if obj_cmp.startswith("flat"):
            return models.ImageType.FLAT
        if obj_cmp.startswith("bias"):
            return models.ImageType.BIAS
        if obj_cmp.startswith("dark"):
            return models.ImageType.DARK
        elif obj_cmp != "":
            # When something is given as the object, assign it type light
            return models.ImageType.LIGHT

    return None



def path_to_file_id(path: Path) -> Optional[str]:
    """
    Generates a unique file id based on the filepath. The general format is:
        <TELESCOPE>/<DATE>/<FILENAME>
    Where the filename is without the fits extension.

    Example paths resolving to the same file_id:
    /net/vega/data/users/observatory/images/160216/STL-6303E/i/160216_Li_00000157.fits
    -> GBT/160216/160216_Li_00000157
    /net/dataserver3/data/users/noelstorr/blaauwastrom/160216/astrom_160216_Li_00000157.fits
    -> GBT/160216/160216_Li_00000157
    """
    p = Path(path)

    # If no telescope is associated with the path, then the path is unknown
    tel = models.Telescope.from_path(p)
    if tel is None:
        return None

    stem = p.stem
    # Strip astrom designation
    stem = stem.strip("astrom_").strip(".astrom")
    file_id_format = "{telescope}/{date}/{filename}"

    file_id = None
    parents = p.parents
    if models.ASTROM_GBT in parents or models.RAW_GBT in parents or models.PIPE_GBT in parents:
        file_id = file_id_format.format(telescope=tel, date=p.parts[7], filename=stem)
    elif models.RAW_LDST in parents:
        file_id = file_id_format.format(telescope=tel, date=p.parts[7], filename=stem)

    return file_id


def get_horizontal(header: dict) -> tuple[Optional[float], Optional[float]]:
    """
    Extracts the alt-az coordinates from the header. Will always be the values from the
    telescope itself.

    If nothing is available will return None
    """
    try:
        # Already in degrees
        return header["CENTALT"], header["CENTAZ"]
    except KeyError:
        return None, None

def get_equitorial(header: dict) -> tuple[Optional[float], Optional[float]]:
    """
    Extracts the equitorial coordinates from the header. If the file has a WCS, it will
    use those coordinates, otherwise it will use the values from the telescope itself.

    If nothing is available will return None
    """
    if "CRVAL1" in header and "CRVAL2" in header:
        return header["CRVAL1"], header["CRVAL2"]
    elif "OBJCTRA" in header and "OBJCTDEC" in header:
        coord: SkyCoord = SkyCoord(header["OBJCTRA"], header["OBJCTDEC"], unit=(u.hourangle, u.deg))
        return coord.ra.degree, coord.dec.degree

    return None, None
