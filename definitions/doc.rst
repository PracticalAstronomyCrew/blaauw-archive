For some comprehensive guides on how to use ADQL look at: http://vo.astro.rug.nl/__system__/adql/query/info.

Some example queries (with what they mean) 
==========================================

Select all observations which have been made in 2020. 
-----------------------------------------------------

::

        SELECT *
        FROM observations.raw
        WHERE date_obs like '2020%'

The ``'like'`` clause is used to check simple regular expressions for strings. ``%`` means match zero or more characters, so this example matches any string which starts with '2020'.

A more specific variant: all observations which have been made on a specific day (this case 18th April 2020)::

        SELECT *
        FROM observations.raw
        WHERE date_obs like '2020-04-18%'

Note that this can be tricky as 'date_obs' is the exact moment of the observation, take this into account!

Select all flat field observations taken in the 'R' filter, sorted by date.
---------------------------------------------------------------------------

::

        SELECT *
        FROM observations.raw
        WHERE filter = 'R' AND imagetyp = 'Flat Frame'
        ORDER BY date_obs

Note the use of AND to combine multiple conditions into one expression. The OR operator is also available.

Select all files with obs_date closest to a given date
------------------------------------------------------

Given some date (in Julian Date format) ``[ref_date]``, query the files which have been taken most recent (past or future) w.r.t. it.

::

        SELECT filename, date_obs, ABS(obs_jd - [ref_date]) AS difference
        FROM observations.raw
        ORDER BY difference

Key feature here is that you can compute your own column (based on simple mathematical expressions) and give them a name using the ``'AS'`` keyword.

A more specific example:
Retrieve the nearest 3x3 binned flat field images to the night of 17th of april 2020 (``2020-04-18T01:25:53.895``, jd: ``2458957.55965156``).

::

        SELECT TOP 10 filename, date_obs, ABS(obs_jd - 2458957.55965156) AS difference
        FROM observations.raw
        WHERE imagetyp = 'Flat Field' AND xbinning = 3 AND ybinning = 3
        ORDER BY difference

Note that there are some issues, as it does not take into account the filter in which the flat field was taken.
Ideally you would want to execute this query for each desired filter (e.g. add: ``WHERE ... AND filter = 'R'``).
In addition, if there are viable flats in the day before and after, the result can be mixed (as the difference is taken absolute).
A possible solution is to compute the same column but without taking the absolute and use that column in some other program.

::

        SELECT TOP 10 filename, date_obs, ABS(obs_jd - 2458957.55965156) AS abs_difference, obs_jd - 2458957.55965156 AS difference
        FROM observations.raw
        WHERE imagetyp = 'Flat Field' AND xbinning = 3 AND ybinning = 3
        ORDER BY abs_difference
