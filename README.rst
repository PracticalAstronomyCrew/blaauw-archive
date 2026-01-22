Blaauw Archive Files
====================

This repository contains the files which are used for the Blaauw Archive.
The Blaauw Archives (currently in development) can be found at:

`vo.astro.rug.nl`_

And a TAP interface is available at:

`https://vo.astro.rug.nl/tap`_

How to Use
==========

There are multiple locations where you can get some help on how to use the
service:

1. TAP Python interface for this service: `Notebook in the examples directory`_
2. `Example queries for the ADQL interface`_


For developers
==============

Overview of components
----------------------

The Blaauw Archive is build upon the `GAVO DaCHS software`_ which
queries an externally managed Postgres database (managed by the code in this repo), and
from this provides the web interface with information and ADQL forms (link above), and
a TAP service. The Postgres database is managed using SQLAlchemy.


The project has the following file structure (some less important components are omitted)

.. code-block:: bash

├── definitions          
│   ├── blaauw.rd        # defines what / how GAVO DaCHS publishes
│   └── doc.rst
├── resources            # Additional info for DaCHS (metadata, logo etc.)
├── Makefile             # High level commands to manage DaCHS and the database
├── scripts              # Scripts for managing the database and obtaining headers
│   ├── crawler.py
│   └── insert.py
└── src                  # General code for interacting with the database
    └── blaauw
        ├── __init__.py
        └── core
            ├── models.py         # defines the database structure
            └── transformers.py   # defines some common operations on a list of headers

Interacting with the database
-----------------------------

Many of the high level interactions can be performed using the `Makefile`:

.. code-block:: bash

   make reload  # reloads the DaCHS service, needed if you updated the RD
   make restart # restarts the DaCHS service, sometimes needed

   make create-db # Removes all data !!! in the database and recreates the structure
   make insert    # Inserts some default data into the database

For the last two, logs can be found under the `logs/` directory, labeled by the
date+time the command was executed.

The original headers are always stored in the FITS files in the respective locations for
GBT or LDST data. To get this information, we use the `crawler.py` script to aggregate
header information in a certain date range into a list of dictionaries with only the
header keyword value pairs, stored as a pickle file.

For example the following will make a list of all GBT observations between Jan
1 2025 up to and including Jan 1 2026, and will store it in the directory `./data`. The
file will have the name: `250101-260101-raw-headers.GBT.pickle`.

.. code-block:: bash

   python3 scripts/crawler.py --output data/ --from-date 250101 --to-date 260101 --base GBT

To insert this into the database, we can insert it with the `insert.py` script:

.. code-block:: bash

   python3 scripts/insert.py --file ./data/250101-260101-raw-headers.GBT.pickle


For all the options see `--help`:

.. code-block:: txt

   $ python3 scripts/crawler.py --help
   usage: crawler.py [-h] [-o OUTPUT] [--date DATE] [--all] [--from-date FROM_DATE] [--to-date TO_DATE] [--base {GBT,LDST}]

   optional arguments:
       -h, --help            show this help message and exit
       -o OUTPUT, --output OUTPUT
                             Location where outputs should be stored. Default is the current directory.
       --date DATE           If specified, will crawl the specific date (format YYMMDD). Default is yesterday.
       --all                 Will crawl the entire base directory, instead of a single day
       --from-date FROM_DATE
                             Specifies the beginning date of the (inclusive) range to search in (format YYMMDD). Also needs an endpoint --to-date.
       --to-date TO_DATE     Specifies the end date of the (inclusive) range to search in (format YYMMDD). Also needs --from-date.
       --base {GBT,LDST}     Defined where the crawler will look for fits files. (default = GBT)


.. _`GAVO DaCHS software`: https://dachs-doc.readthedocs.io/index.html
.. _`Notebook in the examples directory`: ./example/TAPQueries.ipynb
.. _`Example queries for the ADQL interface`: https://vo.astro.rug.nl/browse/blaauw/q
.. _`vo.astro.rug.nl`: http://vo.astro.rug.nl
.. _`http://vo.astro.rug.nl/tap`: http://vo.astro.rug.nl/tap
