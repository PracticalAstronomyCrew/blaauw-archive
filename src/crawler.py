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

pipeline_file_types = {"Raw", "Reduced", "Correction"}


def search(base: str, type: str) -> list:
    """
    base path & the type of image: (Raw, Reduced or Correction)
    """
    if type not in pipeline_file_types:
        raise ValueError(
            f"Type should be one of {pipeline_file_types}, but was '{type}'"
        )

    # List all files of this 'type'
    regex_base = os.path.join(base, "**", type)
    files_iter = glob(
        os.path.join(regex_base, "*.fits"), recursive=True
    ) + glob(os.path.join(regex_base, "*.FIT"), recursive=True)

    return files_iter


def collect(files_iter):
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
    return headers, errors, duration


def split_astrometry(iter):
    astrom_files = filter(
        lambda f: f.endswith("astrom.fits") or f.endswith("astrom.FIT"),
        iter,
    )

    raw_files = filter(
        lambda f: not f.endswith("astrom.fits")
        and not f.endswith("astrom.FIT"),
        iter,
    )
    return list(raw_files), list(astrom_files)


def main():
    BASE_DIR = "/net/dataserver3/data/users/noelstorr/blaauwpipe"

    total_time = process_time()

    for type_name in pipeline_file_types:
        # Seach for the files & collect into a list
        files_iter = search(BASE_DIR, type_name)
        headers, errors, duration = collect(files_iter)

        # Report
        print("Took {}s".format(duration))

        print("")
        print(f"{len(errors)} errors found:")
        for filename, err in errors:
            print(filename, "|", err)

        # Save
        write_name = type_name + "headers.txt"
        print(f"Writing to {write_name}...")
        with open(write_name, "wb") as f:
            dump(headers, f)

    # Report total time
    end_time = process_time()
    total_duration = end_time - total_time
    print(f"The total process took {total_duration}s")


if __name__ == "__main__":
    main()
