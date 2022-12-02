from __future__ import annotations

import argparse
import os
import pickle
import datetime as dt
from pathlib import Path

from itertools import chain
from time import process_time
from typing import Any, Iterable, Optional, Dict


from astropy.io import fits
from tqdm import tqdm  # loading bar

EXCLUDE_SET = {"COMMENT", "HISTORY"}
PIPELINE_FILE_TYPES = {"Raw", "Reduced", "Correction"}
BASE_DIR = "/net/dataserver3/data/users/noelstorr/blaauwpipe"
FITS_EXTENSIONS = {"FIT", "fit", "FITS", "fits"}

HeaderDict = Dict[str, Any]


def header_to_dict(filename: Path) -> HeaderDict:
    """
    Converts the FITS file pointed to by the filename, into a dict of header values.
    It strips unimportant entries, like COMMENT and HISTORY and derives some other
    quantities like the PLATE_SCALE and ODDS from Astrometry.net
    """
    with fits.open(filename) as hdul:
        head_dict = dict(hdul[0].header)

    final_dict = {k: v for k, v in head_dict.items() if k not in EXCLUDE_SET}

    final_dict["FILENAME"] = str(filename.resolve())

    plate_scale = find_plate_scale(head_dict)
    if plate_scale is not None:
        final_dict["PLATE_SCALE"] = plate_scale

    odds = find_odds(head_dict)
    if odds is not None:
        final_dict["ODDS"] = odds

    res = combine_cal_sources(head_dict)
    if res is not None:
        sources, n = res
        final_dict["BP-SRC"] = sources

        # Remove the 'old' entries
        del final_dict[f"BP-SRCN"]
        for i in range(1, n + 1):
            del final_dict[f"BP-SRC{i}"]

    return final_dict


def find_odds(dictionary: HeaderDict) -> Optional[float]:
    """
    Find the odds determined by Astrometry.net

    This value is given inside a COMMENT header, hence we have to search for it
    Will return the odds as a float if it exists, None otherwise.
    """
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


def find_plate_scale(dictionary: HeaderDict) -> Optional[float]:
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


def combine_cal_sources(dictionary: HeaderDict) -> Optional[tuple[list[str], int]]:
    """
    Combines the sources of calibration files into a single list of sources:

    BP-SRCN = 3
    BP-SRC1 = 'path/to/file1'
    BP-SRC2 = 'path/to/file2'
    BP-SRC3 = 'path/to/file3'

    into: [ 'path/to/file1', 'path/to/file2', 'path/to/file3' ]

    If BP-SRCN doesnt exist, or is 0 will return None
    """
    try:
        # TODO: I think BP-SRCN should be a number, not a string
        n = int(dictionary["BP-SRCN"])
    except KeyError or ValueError:
        return None

    if n < 1:
        return None

    sources = [dictionary[f"BP-SRC{i}"] for i in range(1, n + 1)]
    return sources, n


def search(base: Path, ftype: str) -> list[Path]:
    """
    For the given the type of image: (Raw, Reduced or Correction), and base path:
    list all the FITS files under this direction. Roughly:
        {base_path}/**/{ftype}/*.fits
    but for all possible fit extensions (.fit, .FIT, .fits, .FITS)
    """
    if ftype not in PIPELINE_FILE_TYPES:
        raise ValueError(
            f"Type should be one of {PIPELINE_FILE_TYPES}, but was '{ftype}'"
        )

    files_iter = chain.from_iterable(
        base.rglob(f"{ftype}/*.{ext}") for ext in FITS_EXTENSIONS
    )

    return list(files_iter)


def collect(
    files_iter: list[Path], progress_desc: str = ""
) -> tuple[list[HeaderDict], list[tuple[Path, Exception]], float]:
    start_time = process_time()
    headers = []
    errors = []

    # TODO: Make tqdm optional (for when this is called from somewhere else)
    for filename in tqdm(files_iter, ncols=79, desc=progress_desc):
        try:
            head_dict = header_to_dict(filename)
            headers.append(head_dict)
        except Exception as e:
            errors.append((filename, e))

    end_time = process_time()
    duration = end_time - start_time
    return headers, errors, duration


def split_astrometry(iter: Iterable[str]):
    astrom_files = filter(
        lambda f: f.endswith("astrom.fits") or f.endswith("astrom.FIT"),
        iter,
    )

    raw_files = filter(
        lambda f: not f.endswith("astrom.fits") and not f.endswith("astrom.FIT"),
        iter,
    )
    return list(raw_files), list(astrom_files)


def crawl(base_directory: Path) -> dict[str, HeaderDict]:
    result = {}
    for ftype in PIPELINE_FILE_TYPES:
        # Seach for the files & collect into a list
        files_iter = search(base_directory, ftype)
        headers, errors, duration = collect(files_iter, progress_desc=ftype)

        # Store resulting headers
        result[ftype] = headers

        # Report
        print("Took {}s".format(duration))

        if len(errors) > 0:
            print("")
            print(f"{len(errors)} errors found:")

        for filename, err in errors:
            print(filename, "|", err)

    return result


def main() -> None:
    args = parse()

    # Construct the base directory from where to search
    base_directory = Path(BASE_DIR)
    if not args.all:
        if args.date:
            date = args.date
        else:
            date = dt.date.today().strftime("%y%m%d")

        base_directory = base_directory.joinpath(date).resolve()
    else:
        date = "all"

    # and look if it exists
    if not base_directory.is_dir():
        print(f"Base directory {base_directory.absolute()} does not exist.")
        exit(1)

    # Assert that the output directory exists
    output_directory = Path(args.output if args.output else ".").resolve()
    if not output_directory.is_dir():
        print(f"Given output directory {output_directory.absolute()} does not exist.")
        exit(1)

    total_time = process_time()

    result = crawl(base_directory=base_directory)

    # TODO: alternatively, store the entire `result` dict -> copying easier
    for ftype, headers in result.items():
        # Save using pickle
        write_location = output_directory / f"{date}-{ftype.lower()}-headers.pickle"
        print(f"Writing to {write_location}...")
        with open(write_location, "wb") as f:
            pickle.dump(headers, f)

    # Report total time
    end_time = process_time()
    total_duration = end_time - total_time
    print(f"The total process took {total_duration}s")


def parse() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        help="Location where outputs should be stored. Default is the current directory.",
    )
    parser.add_argument(
        "--date",
        type=str,
        help="If specified, will crawl the specific date (format YYMMDD). Default is today",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Will crawl the entire base directory, instead of a single day",
    )
    # TODO: Add configurable base directory
    return parser.parse_args()


if __name__ == "__main__":
    main()
