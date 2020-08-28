<!-- 
vim: ft=xml 
vim:et:sta:sw=2  
-->
<resource schema="observations">
  <meta name="title">Raw Observation Data</meta>
  <meta name="creationDate">2020-05-13</meta>
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
    For some comprehensive guides on how to use ADQL look at: http://stensipma.com/__system__/adql/query/info.

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

  </meta>

  <table id="raw" onDisk="True" adql="True" mixin="//scs#pgs-pos-index">

    <column name="id" type="bigint" unit="" ucd="meta.id;meta.main" required="True">
      <description>Database identifier of the file.</description></column>

    <column name="ra" type="double precision" unit="deg"  ucd="pos.eq.ra;meta.main">
      <description>Right Ascention (degrees) coordinate of where the telescope is pointed. Derived from 'OBJCTRA'.</description></column>
    <column name="dec" type="double precision" unit="deg"  ucd="pos.eq.dec;meta.main">
      <description>Declination (degrees) coordinate of where the telescope is pointed. Derived from 'OBJCTDEC'.</description></column>
    <column name="obs_jd" type="double precision" unit="d" ucd="time.epoch;obs">
      <description>Observation date and time as Julian Date (JD). Derived from 'DATE_OBS'.</description></column>
    <column name="filename" type="text" unit="" ucd="meta.id;meta.file">
      <description>Absolute path to the corresponding fits file on the Vega data server.</description></column>

    <column name="IMAGETYP" type="text"             unit=""  ucd="meta.code;obs"><description>The type of image, e.g. 'Light Frame', 'Dark Frame', 'Bias Frame' or 'Flat Frame'.</description></column>
    <column name="DATE_OBS" type="text"             unit=""  ucd=""><description>Datetime string of the moment the observation was taken (in UTC). See 'obs_jd' column for the same time in Julian Days.</description></column>
    <column name="OBJECT"   type="text"             unit=""  ucd=""><description>Name of the (intended) object being observed.</description></column>
    <column name="OBJCTRA"  type="text"             unit=""  ucd=""><description>Estimated center right ascention coordinate of the image.</description></column>
    <column name="OBJCTDEC" type="text"             unit=""  ucd=""><description>Estimated center declination coordinate of the image.</description></column>
    <column name="FILTER"   type="text"             unit=""  ucd="meta.code;instr.filter"><description>The name of the filter used in the Observation</description></column>
    <column name="EXPTIME"  type="double precision" unit="s" ucd=""><description>Exposure time of the observation (in seconds)</description></column>
    <column name="EXPOSURE" type="double precision" unit="s" ucd=""><description>Exposure time of the observation (in seconds)</description></column>
    <column name="AIRMASS"  type="double precision" unit=""  ucd=""><description>No Description (TODO)</description></column>

    <column name="SIMPLE"      type="bigint"           unit="" ucd=""><description>No Description (TODO)</description></column>
    <column name="BITPIX"      type="bigint"           unit="" ucd=""><description>No Description (TODO)</description></column>
    <column name="NAXIS"       type="bigint"           unit="" ucd=""><description>No Description (TODO)</description></column>
    <column name="NAXIS1"      type="bigint"           unit="" ucd=""><description>No Description (TODO)</description></column>
    <column name="NAXIS2"      type="bigint"           unit="" ucd=""><description>No Description (TODO)</description></column>
    <column name="BSCALE"      type="double precision" unit="" ucd=""><description>No Description (TODO)</description></column>
    <column name="BZERO"       type="double precision" unit="" ucd=""><description>No Description (TODO)</description></column>
    <column name="BIAS"        type="bigint"           unit="" ucd=""><description>No Description (TODO)</description></column>
    <column name="FOCALLEN"    type="double precision" unit="" ucd=""><description>No Description (TODO)</description></column>
    <column name="APTAREA"     type="double precision" unit="" ucd=""><description>No Description (TODO)</description></column>
    <column name="APTDIA"      type="double precision" unit="" ucd=""><description>No Description (TODO)</description></column>
    <column name="TIME_OBS"    type="text"             unit="" ucd=""><description>No Description (TODO)</description></column>
    <column name="SWCREATE"    type="text"             unit="" ucd=""><description>No Description (TODO)</description></column>
    <column name="SET_TEMP"    type="double precision" unit="" ucd=""><description>No Description (TODO)</description></column>
    <column name="COLORCCD"    type="bigint"           unit="" ucd=""><description>No Description (TODO)</description></column>
    <column name="DISPCOLR"    type="bigint"           unit="" ucd=""><description>No Description (TODO)</description></column>
    <column name="CCDSFPT"     type="bigint"           unit="" ucd=""><description>No Description (TODO)</description></column>
    <column name="XORGSUBF"    type="bigint"           unit="" ucd=""><description>No Description (TODO)</description></column>
    <column name="YORGSUBF"    type="bigint"           unit="" ucd=""><description>No Description (TODO)</description></column>
    <column name="CCDSUBFL"    type="bigint"           unit="" ucd=""><description>No Description (TODO)</description></column>
    <column name="CCDSUBFT"    type="bigint"           unit="" ucd=""><description>No Description (TODO)</description></column>
    <column name="XBINNING"    type="bigint"           unit="" ucd=""><description>No Description (TODO)</description></column>
    <column name="CCDXBIN"     type="bigint"           unit="" ucd=""><description>No Description (TODO)</description></column>
    <column name="YBINNING"    type="bigint"           unit="" ucd=""><description>No Description (TODO)</description></column>
    <column name="CCDYBIN"     type="bigint"           unit="" ucd=""><description>No Description (TODO)</description></column>
    <column name="EXPSTATE"    type="bigint"           unit="" ucd=""><description>No Description (TODO)</description></column>
    <column name="CCD_TEMP"    type="double precision" unit="" ucd=""><description>No Description (TODO)</description></column>
    <column name="TEMPERAT"    type="double precision" unit="" ucd=""><description>No Description (TODO)</description></column>
    <column name="TELTKRA"     type="double precision" unit="" ucd=""><description>No Description (TODO)</description></column>
    <column name="TELTKDEC"    type="double precision" unit="" ucd=""><description>No Description (TODO)</description></column>
    <column name="CENTAZ"      type="double precision" unit="" ucd=""><description>No Description (TODO)</description></column>
    <column name="CENTALT"     type="double precision" unit="" ucd=""><description>No Description (TODO)</description></column>
    <column name="TELHA"       type="text"             unit="" ucd=""><description>No Description (TODO)</description></column>
    <column name="LST"         type="text"             unit="" ucd=""><description>No Description (TODO)</description></column>
    <column name="SITELAT"     type="text"             unit="" ucd=""><description>No Description (TODO)</description></column>
    <column name="SITELONG"    type="text"             unit="" ucd=""><description>No Description (TODO)</description></column>
    <column name="INSTRUME"    type="text"             unit="" ucd=""><description>No Description (TODO)</description></column>
    <column name="EGAIN"       type="double precision" unit="" ucd=""><description>No Description (TODO)</description></column>
    <column name="E_GAIN"      type="double precision" unit="" ucd=""><description>No Description (TODO)</description></column>
    <column name="XPIXSZ"      type="double precision" unit="" ucd=""><description>No Description (TODO)</description></column>
    <column name="YPIXSZ"      type="double precision" unit="" ucd=""><description>No Description (TODO)</description></column>
    <column name="SBIGIMG"     type="bigint"           unit="" ucd=""><description>No Description (TODO)</description></column>
    <column name="USER_2"      type="text"             unit="" ucd=""><description>No Description (TODO)</description></column>
    <column name="DATAMAX"     type="bigint"           unit="" ucd=""><description>No Description (TODO)</description></column>
    <column name="SBSTDVER"    type="text"             unit="" ucd=""><description>No Description (TODO)</description></column>
    <column name="CBLACK"      type="bigint"           unit="" ucd=""><description>No Description (TODO)</description></column>
    <column name="CWHITE"      type="bigint"           unit="" ucd=""><description>No Description (TODO)</description></column>
    <column name="CTYPE1"      type="text"             unit="" ucd=""><description>No Description (TODO)</description></column>
    <column name="CTYPE2"      type="text"             unit="" ucd=""><description>No Description (TODO)</description></column>
    <column name="EQUINOX"     type="double precision" unit="" ucd=""><description>No Description (TODO)</description></column>
    <column name="CRVAL1"      type="double precision" unit="" ucd=""><description>No Description (TODO)</description></column>
    <column name="CRVAL2"      type="double precision" unit="" ucd=""><description>No Description (TODO)</description></column>
    <column name="CRPIX1"      type="double precision" unit="" ucd=""><description>No Description (TODO)</description></column>
    <column name="CRPIX2"      type="double precision" unit="" ucd=""><description>No Description (TODO)</description></column>
    <column name="CUNIT1"      type="text"             unit="" ucd=""><description>No Description (TODO)</description></column>
    <column name="CUNIT2"      type="text"             unit="" ucd=""><description>No Description (TODO)</description></column>
    <column name="CD1_1"       type="double precision" unit="" ucd=""><description>No Description (TODO)</description></column>
    <column name="CD1_2"       type="double precision" unit="" ucd=""><description>No Description (TODO)</description></column>
    <column name="CD2_1"       type="double precision" unit="" ucd=""><description>No Description (TODO)</description></column>
    <column name="CD2_2"       type="double precision" unit="" ucd=""><description>No Description (TODO)</description></column>
    <column name="PLATE_SCALE" type="double precision" unit="" ucd=""><description>No Description (TODO)</description></column>
  </table>

  <service id="cone" allowed="scs.xml,form">
    <meta name='title'>Observations cone search</meta>
    <meta name='shortName'>Obs Cone</meta>
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

