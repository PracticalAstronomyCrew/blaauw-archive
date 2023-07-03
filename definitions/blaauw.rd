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
    Some example queries (with what they mean) 
    ==========================================

    OUT OF DATE!!

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
      <description>Right Ascention coordinate of where the telescope is pointed.</description></column>
    <column name="dec" type="double precision" unit="deg"  ucd="pos.eq.dec;meta.main">
      <description>Declination coordinate of where the telescope is pointed.</description></column>
    <column name="alt" type="double precision" unit="deg"  ucd="pos.eq.alt">
      <description>Alt-azimutal altitude</description></column>
    <column name="azimuth" type="double precision" unit="deg"  ucd="pos.az.azi">
      <description>Alt-azimutal azimut</description></column>

    <column name="date_mjd" type="double precision" unit="d" ucd="time.epoch;obs">
      <description>Observation date and time as Modified Julian Date (MJD). Derived from the 'DATE_OBS' keyword.</description></column>
    <column name="date" type="double precision" unit="d" ucd="time.epoch;obs">
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
    <column name="binning" type="int" unit="" ucd="">
      <description>The binning of the CCD (typically 1).</description></column>
    <column name="airmass" type="float" unit="" ucd="">
      <description>Airmass of the observation</description></column>
    <!-- <column name="OBJECT"   type="text"             unit=""  ucd=""><description></description></column> -->
    <!-- <column name="OBJCTRA"  type="text"             unit=""  ucd=""><description>Estimated center right ascention coordinate of the image.</description></column> -->
    <!-- <column name="OBJCTDEC" type="text"             unit=""  ucd=""><description>Estimated center declination coordinate of the image.</description></column> -->

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

