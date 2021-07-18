from astropy.io import fits

EXCLUDE_SET = {"COMMENT", "HISTORY"}


def header_to_dict(filename):
    with fits.open(filename) as hdul:
        head_dict = dict(hdul[0].header)

    final_dict = {k: v for k, v in head_dict.items() if k not in EXCLUDE_SET}

    final_dict["FILENAME"] = filename

    plate_scale = find_plate_scale(head_dict)
    if plate_scale is not None:
        final_dict["PLATE_SCALE"] = plate_scale

    odds = find_odds(head_dict)
    if odds is not None:
        final_dict["ODDS"] = odds

    return final_dict


def find_odds(dictionary):
    try:
        comment_entry = dictionary["COMMENT"]
    except KeyError:
        return None

    for line in comment_entry:
        str_line = line.strip()
        if str_line.startswith("odds: "):
            break
    else:
        return None

    odds = float(line.split(" ")[1])
    return odds


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
        str_line = line.strip()
        if str_line.startswith("scale: ") and str_line.endswith(" arcsec/pix"):
            break
    else:
        return None

    plate_scale = float(line.split(" ")[1])
    return plate_scale


from glob import glob
import os
from tqdm import tqdm  # loading bar
from time import process_time
from pickle import dump


def main():
    BASE_DIR = "/net/dataserver3/data/users/noelstorr/blaauwastrom/"

    files_iter = glob(
        os.path.join(BASE_DIR, "**/*.fits"), recursive=True
    ) + glob(os.path.join(BASE_DIR, "**/*.FIT"), recursive=True)
    # files_iter = files_iter[:10]

    start_time = process_time()
    headers = []
    errors = []

    for filename in tqdm(files_iter, ncols=79):
        try:
            head_dict = header_to_dict(filename)
            headers.append(head_dict)
        except Exception as e:
            errors.append((filename, e))

    end_time = process_time()
    duration = end_time - start_time
    print("Took {}s".format(duration))

    print("")
    print(f"{len(errors)} errors found:")
    for filename, err in errors:
        print(filename, "|", err)

    write_name = "headers.txt"
    print(f"Writing to {write_name}...")
    with open(write_name, "wb") as f:
        dump(headers, f)


if __name__ == "__main__":
    main()
