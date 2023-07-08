<!-- 
vim: ft=xml 
vim:et:sta:sw=2  
-->
<resource schema="blaauw">
  <meta name="title">Raw Observation Data</meta>
  <meta name="creationDate">2023-07-03</meta>
  <meta name="description">
    This database contains the header information of the raw observations made in the Blaauw Observatory. It is currently in heavy development!
  </meta>
  <meta name="creator">Sten Sipma</meta>
  <meta name="subject">Raw Observations</meta>
  <meta name="subject">Bias Frames</meta>
  <meta name="subject">Dark Frames</meta>
  <meta name="subject">Flat Frames</meta>
  <meta name="subject">Target Frames</meta>
  <meta name="subject">FITS Headers</meta>
  <meta name="type">Archive</meta>
  <!-- <meta name=""></meta> -->

  <meta name="_longdoc" format="rst">
It is recommended to query the archive using another program via TAP, like
TOPCAT or Python. Some examples on how to work with the database from Python
is given in the example `TAP Queries Notebook`_ .

For some comprehensive guides on how to use ADQL look at the `ADQL tutorial`_ .


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

   * - 2018
     - 2019
     - 2020
     - 2021
     - 2022
     - 2023
     - 2024
     - 2025
   * - 58119
     - 58484
     - 58849
     - 59215
     - 59580
     - 59945
     - 60310
     - 60676

A more specific variant: all observations which have been made on a specific day (this case 18th April 2020).
Using the calculator we find that the MJD is 58957, which will be 18th of April at 00:00, so it refers to the night 17-18 in April.
We therefore need to add half a day (18th at noon) for the lower limit, and add 1.5 days for the upper limit (19th at noon).::

        SELECT *
        FROM blaauw.raw
        WHERE date_obs_mjd between (58957 + 0.5) and (58957 + 1.5)

Note that this can be tricky as 'date_obs_mjd' is the exact moment of the observation, take this into account!

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

Given some date (in MJD format) ``[ref_date]``, query the files which have been taken most recent (past or future) w.r.t. it.

::

        SELECT filename, date_obs_mjd, ABS(date_obs_mjd - [ref_date]) AS difference
        FROM blaauw.raw
        ORDER BY difference

Key feature here is that you can compute your own column (based on simple mathematical expressions) and give them a name using the ``'AS'`` keyword.

A more specific example: Retrieve the nearest 3x3 binned flat field images to the night of 17th of april 2020 (``2020-04-18 00:00:00``, MJD: ``58957``).

::

        SELECT TOP 10 filename, date_obs_mjd, ABS(date_obs_mjd - 58957) AS difference
        FROM blaauw.raw
        WHERE image_type = 'FLAT' AND binning = 3
        ORDER BY difference

Note that there are some issues, as it does not take into account the filter in which the flat field was taken.
Ideally you would want to execute this query for each desired filter (e.g. add: ``WHERE ... AND filter = 'R'``).
In addition, if there are viable flats in the day before and after, the result can be mixed (as the difference is taken absolute).
A possible solution is to compute the same column but without taking the absolute and use that column in some other program. 

::

        SELECT TOP 10 filename, date_obs, ABS(date_obs_mjd - 58957) AS abs_difference, date_obs_mjd - 58957 AS difference
        FROM blaauw.raw
        WHERE image_type = 'FLAT' AND binning = 3
        ORDER BY abs_difference

How to use this query in another program (Python) is one of the examples in the `TAP Queries Notebook`_ .

.. _TAP Queries Notebook: https://github.com/PracticalAstronomyCrew/blaauw-archive/blob/master/example/TAPQueries.ipynb
.. _ADQL tutorial: https://vo.astro.rug.nl/__system__/adql/query/info

  </meta>

  <table id="raw" onDisk="True" adql="True" mixin="//scs#pgs-pos-index">
    <column name="file_id" type="text" unit="" ucd="meta.id;meta.file;meta.main">
      <description>Combination of the folder date and file name to compare raw and processed files.</description></column>
    <column name="ra" type="double precision" unit="deg"  ucd="pos.eq.ra;meta.main">
      <description>Right Ascention coordinate of where the telescope is pointed.</description></column>
    <column name="dec" type="double precision" unit="deg"  ucd="pos.eq.dec;meta.main">
      <description>Declination coordinate of where the telescope is pointed.</description></column>
    <column name="alt" type="double precision" unit="deg"  ucd="pos.eq.alt">
      <description>Alt-azimutal altitude</description></column>
    <column name="az" type="double precision" unit="deg"  ucd="pos.az.azi">
      <description>Alt-azimutal azimut</description></column>

    <column name="date_obs_mjd" type="double precision" unit="d" ucd="time.epoch;obs">
      <description>Observation date and time as Modified Julian Date (MJD). Derived from the 'DATE_OBS' keyword.</description></column>
    <column name="date_obs" type="timestamp" unit="" ucd="time.epoch;obs">
      <description>Observation date and time in UTC.</description></column>

    <column name="filename" type="text" unit="" ucd="meta.id;meta.file">
      <description>Absolute path to the corresponding fits file on the Vega data server.</description></column>

    <column name="telescope" type="text" unit="" ucd="instr.tel">
      <description>The telescope which produced the observation, either: GBT (Gratema Bernoulli Telescope) or LDST (Lauwersmeer Dark Sky Telescope).</description></column>
    <column name="instrument" type="text" unit="" ucd="instr.instr">
      <description>Instrument / Detection which produced the observation.</description></column>

    <column name="image_type" type="text" unit="" ucd="meta.code;obs">
      <description>The type of image, e.g. 'Light', 'Dark', 'Bias' or 'Flat'.</description></column>

    <column name="filter" type="text" unit="" ucd="meta.code;instr.filter">
      <description>The name of the filter used in the Observation.</description></column>
    <column name="target_object" type="text" unit="" ucd="">
      <description>Name of the (intended) object being observed.</description></column>
    <column name="exposure_time" type="double precision" unit="s" ucd="time.duration;obs.exposure">
      <description>Exposure time of the observation (in seconds).</description></column>
    <column name="binning" type="smallint" unit="" ucd="">
      <description>The binning of the CCD (typically 1).</description></column>
    <column name="airmass" type="double precision" unit="" ucd="obs.airmass">
      <description>Airmass of the observation</description></column>

    <column name="created_at" type="timestamp" unit="" ucd="time.creation">
      <description>Datetime on which the entry was first inserted into the database.</description></column>
    <column name="updated_at" type="timestamp" unit="" ucd="time.creation">
      <description>Datetime on which the entry last updated.</description></column>
    <column name="id" type="bigint" unit="" ucd="meta.id;meta.main" required="True">
      <description>Database identifier of the file.</description></column>
  </table>

  <service id="raw-cone" allowed="scs.xml,form">
    <meta name='title'>Cone Search for raw Observations</meta>
    <meta name='shortName'>Cone Raw</meta>
    <meta name='testQuery.ra'>51</meta>
    <meta name='testQuery.dec'>0</meta>
    <meta name='testQuery.sr'>0.01</meta>
    <scsCore queriedTable="raw">
        <FEED source="//scs#coreDescs"/>
    </scsCore>
  </service>
  

  <data id="d" updating="True">
    <publish sets="local"/>
    <make table="raw"/>
  </data>

</resource>
