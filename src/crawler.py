from astropy.io import fits

EXCLUDE_SET = {"COMMENT", "HISTORY"}


def header_to_dict(filename):
    with fits.open(filename) as hdul:
        head_dict = dict(hdul[0].header)

    final_dict = {k: v for k, v in head_dict.items() if k not in EXCLUDE_SET}

    final_dict["FILENAME"]
    plate_scale = find_plate_scale(head_dict)
    if plate_scale is not None:
        final_dict["PLATE_SCALE"] = plate_scale


def find_plate_scale(dictionary):
    """
    Find the plate scale determined by Astrometry.net
    
    This value is given inside a COMMENT header, hence we have to search for it
    Will return the plate scale as a float if it exists, None otherwise.
    """
    try:
        comment_entry = dictionary["COMMENT"]
    except KeyError:
        return None

    for line in comment_entry:
        if line.startswith("scale: ") and line.endswith(" arcsec/pixel"):
            break
    else:
        return None

    plate_scale = float(line.split(" ")[1])
    return plate_scale
