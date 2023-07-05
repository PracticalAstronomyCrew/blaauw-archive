from __future__ import annotations

import argparse
import os
import re
import pickle
import datetime as dt
from pathlib import Path

from itertools import chain
from time import process_time
from typing import Any, Iterable, List, Optional, Dict


from astropy.io import fits
from tqdm import tqdm

from blaauw.core.models import BASE_DIR_MAP, PIPE_GBT  # loading bar

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


def search(base: Path, ftype: Optional[str] = None) -> list[Path]:
    """
    For the given the type of image: (Raw, Reduced or Correction), and base path:
    list all the FITS files under this direction. Roughly:
        {base_path}/**/{ftype}/*.fits
    but for all possible fit extensions (.fit, .FIT, .fits, .FITS)

    If ftype is not specified, will just search
        {base_path}/**/*.fits
    """
    if ftype is None:
        files_iter = chain.from_iterable(
            base.rglob(f"*.{ext}") for ext in FITS_EXTENSIONS
        )
    else:
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
    # TODO: not used?
    astrom_files = filter(
        lambda f: f.endswith("astrom.fits") or f.endswith("astrom.FIT"),
        iter,
    )

    raw_files = filter(
        lambda f: not f.endswith("astrom.fits") and not f.endswith("astrom.FIT"),
        iter,
    )
    return list(raw_files), list(astrom_files)


def crawl(search_dirs: List[Path], pipeline=False) -> dict[str, List[HeaderDict]]:
    result = {}
    if pipeline:
        for ftype in PIPELINE_FILE_TYPES:
            # Seach for the files & collect into a list
            files_iter = []
            for search_dir in search_dirs:
                files_iter.extend(search(search_dir, ftype))
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
    else:
        # Seach for the files & collect into a list
        files_iter = []
        for search_dir in search_dirs:
            files_iter.extend(search(search_dir))
        headers, errors, duration = collect(files_iter, progress_desc="All")

        # Store resulting headers
        result['Raw'] = headers

        # Report
        print("Took {}s".format(duration))

        if len(errors) > 0:
            print("")
            print(f"{len(errors)} errors found:")

        for filename, err in errors:
            print(filename, "|", err)

    return result

DIR_EXEPTIONS = {"2222-22-22", "FISHEYE JAKE 20230407"}

def main() -> None:
    args = parse()

    # Assert that the output directory exists
    output_directory = Path(args.output if args.output else ".").resolve()
    if not output_directory.is_dir():
        print(f"Given output directory {output_directory.absolute()} does not exist.")
        exit(1)

    # Construct the base directory from where to search (given as an argument)
    base_directory = Path(BASE_DIR_MAP[args.base])

    print(f"Indexing dates in {base_directory}...")
    # List all valid dates in that directory
    date_re = re.compile(r"([0-9][0-9])?([0-9][0-9]-?[0-9][0-9]-?[0-9][0-9])")
    children = list(base_directory.iterdir())
    dates = []
    for child in children:
        if child.name in DIR_EXEPTIONS:
            print(f"Skipping {child}: exception...")
            continue
        match = date_re.match(child.name)
        if match is None:
            print(f"Skipping {child.name}: not matched...")
            continue
        date_str = match.groups()[-1] # match the last group
        date_str = date_str.replace("-", "")
        date = dt.datetime.strptime(date_str, "%y%m%d").date() # format: YYMMDD
        # print(f"parsed: {date} from {child}")
        dates.append((date, child))

    dates.sort()
    # Now we have a list with tuples: (date, path). Note that date is not unique!

    # Now we have 3 cases:
    # 1. We want to seach everything (--all) 
    #    --> We can just seach all the listed directories
    # 2. We want to search a specific date (--date)
    #    --> Find the matching date(s) in the list
    # 3. We want to search range of dates (--from, --to)
    #    --> Find the dates in the range

    # Case 1.
    search_dirs = []
    if args.all:
        print(f"Running for all dates")
        search_dirs = [d[1] for d in dates]
        outfile_date = "all"
    # Case 3.
    elif args.to_date is not None and args.from_date is not None:
        print(f"Running for range: {args.from_date} - {args.to_date}")
        search_dirs = [d[1] for d in dates if d[0] >= args.from_date and d[0] <= args.to_date]
        outfile_date = f"{args.from_date.strftime('%y%m%d')}-{args.to_date.strftime('%y%m%d')}"
    # Case 2.
    else:
        print(f"Running for single date: {args.date}")
        search_dirs = [d[1] for d in dates if d[0] == args.date]
        outfile_date = args.date.strftime('%y%m%d')
    
    # print("To search")
    # for d in search_dirs:
    #     print(d)

    total_time = process_time()

    pipeline = PIPE_GBT == base_directory
    result = crawl(search_dirs, pipeline)

    # TODO: alternatively, store the entire `result` dict -> copying easier
    for ftype, headers in result.items():
        # Save using pickle
        write_location = output_directory / f"{outfile_date}-{ftype.lower()}-headers.pickle"
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
        type=lambda s: dt.datetime.strptime(s, "%y%m%d").date(),
        help="If specified, will crawl the specific date (format YYMMDD). Default is yesterday.",
        default=dt.date.today() - dt.timedelta(days=1),
        # TODO: add some default
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Will crawl the entire base directory, instead of a single day",
    )
    parser.add_argument(
        "--from-date",
        type=lambda s: dt.datetime.strptime(s, "%y%m%d").date(),
        help="Specifies the beginning date of the (inclusive) range to search in (format YYMMDD). Also needs an endpoint --to-date.",
    )
    parser.add_argument(
        "--to-date",
        type=lambda s: dt.datetime.strptime(s, "%y%m%d").date(),
        help="Specifies the end date of the (inclusive) range to search in (format YYMMDD). Also needs --from-date.",
    )
    parser.add_argument(
            "--base",
            type=str,
            choices=list(BASE_DIR_MAP.keys()),
            default="RAW_GBT",
            help="Defined where the crawler will look for fits files.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    main()


