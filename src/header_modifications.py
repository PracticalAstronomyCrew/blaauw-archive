from pathlib import Path
from typing import Optional

from astropy.time import Time
from astropy.coordinates import SkyCoord
from astropy import units as u


def path_to_file_id(path: str, strip_astrom: bool = True) -> Optional[str]:
    """
    Example paths resolving to the same file_id:
    /net/vega/data/users/observatory/images/160216/STL-6303E/i/160216_Li_00000157.fits
    -> 160216/160216_Li_00000157
    /net/dataserver3/data/users/noelstorr/blaauwastrom/160216/astrom_160216_Li_00000157.fits
    -> 160216/160216_Li_00000157 (with strip_astrom=True)
    """
    p = Path(path)

    stem = p.stem
    if strip_astrom:
        stem = stem.strip("astrom_").strip(".astrom")

    file_id = None
    if "blaauwastrom" in p.parts:
        file_id = p.parts[7] + "/" + stem
    elif "observatory" in p.parts:
        file_id = p.parts[7] + "/" + stem
    elif "blaauwpipe":
        file_id = p.parts[7] + "/" + stem

    return file_id


def add_file_id(head: dict) -> None:
    """
    Add the header 'file_id' to the header, which is the combination of date
    and filename (without full path). It is used to compare processed and
    uprocessed files, to ensure there are no duplicates in there.
    """
    if "FILENAME" in head:
        fn = head["FILENAME"]
        file_id = path_to_file_id(fn)
        if file_id is not None:
            head["file_id"] = file_id


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
        coord = SkyCoord(head["OBJCTRA"], head["OBJCTDEC"], unit=(u.hourangle, u.deg))
        head["ra"], head["dec"] = coord.ra.degree, coord.dec.degree
