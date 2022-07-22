from astropy.time import Time
from astropy.coordinates import SkyCoord
from astropy import units as u


def add_file_id(head: dict) -> None:
    """
    Add the header 'file_id' to the header, which is the combination of date
    and filename (without full path). It is used to compare processed and
    uprocessed files, to ensure there are no duplicates in there.
    """
    if "FILENAME" in head:
        fn = head["FILENAME"]
        splitted = fn.split("/")
        if "blaauwastrom" in fn:
            head["file_id"] = splitted[7] + "/" + splitted[8]
        else:
            head["file_id"] = splitted[7] + "/" + splitted[10]


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
