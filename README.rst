Blaauw Archive Files
====================

This repository contains the files which are used for the Blaauw Archive.  
The Blaauw Archives (currently in development) can be found at:

`vo.astro.rug.nl`_

And a tap interface is available at:

`https://vo.astro.rug.nl/tap`_

Overview of insertion
---------------------


1. Load the file with headers. This should be a list of dicts: list[dict],
where each dict contains the header information of the FITS file.

2. for each file/header

3. determine what the 'type' it is
        - A raw file. Can be light,bias,flat,dark (all accepted)
        - A processed file, either:
        - master (flat, dark, bias)
        - reduced (light)

4. Insert the file in database based on type
        - raw file      -> raw
            As before
        - master        -> calibration
            - Get reference to the raw version (KW-TRAW / KW-PRAW) (maybe get
                    the actual database ID)
            - Get reference to the masters used to create it (i.e. a master
              dark uses a master bias). 
              NOTE:
            - Insert into calibration
            - Get references to the components of the master (KW-SRCN &
                    KW-SRC#>)& add entry in the composition table
        - reduced light -> reduced
            - Get reference to the raw version (KW-TRAW / KW-PRAW) (maybe get
                    the actual database ID)
            - Get reference to the masters used to create it (i.e. a master
                    dark uses a master bias)
            - Insert into reduced

Usage
-----

There are multiple locations where you can get some help on how to use the
service: 

1. TAP Python interface for this service: `Notebook in the examples directory`_
2. `Basic introduction to the Raw Observations table`_

Contributing
------------

If you want to add something to the Blaauw Archive, you can add some
description to columns in `this CSV File`_ or add something to the
`description of the raw data table`_.

.. _`this CSV File`: ./definitions/column-list.csv
.. _`description of the raw data table`: ./definitions/doc.rst
.. _`Notebook in the examples directory`: ./example/TAPQueries.ipynb 
.. _`Basic introduction to the Raw Observations table`: http://vo.astro.rug.nl/browse/observations/q
.. _`vo.astro.rug.nl`: http://vo.astro.rug.nl
.. _`http://vo.astro.rug.nl/tap`: http://vo.astro.rug.nl/tap
