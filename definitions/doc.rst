It is recommended to query the archive using another program via TAP, like
TOPCAT or Python. Some examples on how to work with the database from Python is given
in the example `Queries Notebook https://github.com/PracticalAstronomyCrew/blaauw-archive/blob/master/example/TAPQueries.ipynb`_.`

For some comprehensive guides on how to use ADQL look at `this tutorial
http://vo.astro.rug.nl/__system__/adql/query/info`_.

Some example queries (with what they mean) 
==========================================

Select all observations which have been made in 2020. 
-----------------------------------------------------

::

        SELECT *
        FROM blaauw.raw
        WHERE date_obs_mjd between 58849 and 59215

The best way to compare dates is to use the ``date_obs_mjd`` (date of the observation in Modified Julian days).
A convenient calculator is: https://mjdconverter.com/. Here 2020 (first of January 00h) refers to 58849, 2021 to 59215.
Some common values are:

.. list-table:: Useful MJD Values
   :widths: auto
   :header-rows: 1

   * - Year
     - MJD
   * - 2018
     - 58119
   * - 2019
     - 58484
   * - 2020
     - 58849
   * - 2021
     - 59215
   * - 2022
     - 59580
   * - 2023
     - 59945
   * - 2024
     - 60310
   * - 2025
     - 60676

A more specific variant: all observations which have been made on a specific
day (this case 18th April 2020). Using the calculator we find that the MJD is
58957, which will be 18th of April at 00:00, so it refers to the night 17-18 in
April. We therefore need to add half a day (18th at noon) for the lower limit,
and add 1.5 days for the upper limit (19th at noon).::

        SELECT *
        FROM blaauw.raw
        WHERE date_obs_mjd between (58957 + 0.5) and (58957 + 1.5)

Note that this can be tricky as 'date_obs_mjd' is the exact moment of the
observation, take this into account!

Flat Fields in R of GBT
-----------------------

::

        SELECT *
        FROM blaauw.raw
        WHERE filter = 'R' AND image_type = 'FLAT' AND telescope = 'GBT'
        ORDER BY date_obs

Note the use of AND to combine multiple conditions into one expression. The OR operator is also available.

Select all files with obs_date closest to a given date
------------------------------------------------------

Given some date (in MJD format) ``[ref_date]``, query the files which have been
taken most recent (past or future) w.r.t. it.

::

        SELECT filename, date_obs_mjd, ABS(date_obs_mjd - [ref_date]) AS difference
        FROM blaauw.raw
        ORDER BY difference

Key feature here is that you can compute your own column (based on simple
mathematical expressions) and give them a name using the ``'AS'`` keyword.

A more specific example: Retrieve the nearest 3x3 binned flat field images to
the night of 17th of april 2020 (``2020-04-18 00:00:00``, MJD:
``58957``).

::

        SELECT TOP 10 filename, date_obs_mjd, ABS(date_obs_mjd - 58957) AS difference
        FROM blaauw.raw
        WHERE image_type = 'FLAT' AND binning = 3
        ORDER BY difference

Note that there are some issues, as it does not take into account the filter in
which the flat field was taken. Ideally you would want to execute this query
for each desired filter (e.g. add: ``WHERE ... AND filter = 'R'``). In
addition, if there are viable flats in the day before and after, the result can
be mixed (as the difference is taken absolute). A possible solution is to
compute the same column but without taking the absolute and use that column in
some other program. 

::

        SELECT TOP 10 filename, date_obs, ABS(date_obs_mjd - 58957) AS abs_difference, date_obs_mjd - 58957 AS difference
        FROM blaauw.raw
        WHERE image_type = 'FLAT' AND binning = 3
        ORDER BY abs_difference

How to use this query in another program (Python) is one of the examples in the `TAP Queries Notebook https://github.com/PracticalAstronomyCrew/blaauw-archive/blob/master/example/TAPQueries.ipynb`_.
