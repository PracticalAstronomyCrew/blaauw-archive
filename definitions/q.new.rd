<!-- 
vim: ft=xml 
vim:et:sta:sw=2  
-->
<resource schema="observations">
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
    
    <!-- Headers here ... -->

  </table>

  <table id="all" onDisk="True" adql="True" mixin="//scs#pgs-pos-index">
    <column name="id" type="bigint" unit="" ucd="meta.id;meta.main" required="True">
      <description>Database identifier of the file.</description></column>

    <column name="ra" type="double precision" unit="deg"  ucd="pos.eq.ra;meta.main">
      <description>Right Ascention (degrees) coordinate of where the telescope is pointed. Derived from 'OBJCTRA'.</description></column>
    <column name="dec" type="double precision" unit="deg"  ucd="pos.eq.dec;meta.main">
      <description>Declination (degrees) coordinate of where the telescope is pointed. Derived from 'OBJCTDEC'.</description></column>
    <column name="obs_jd" type="double precision" unit="d" ucd="time.epoch;obs">
      <description>Observation date and time as Julian Date (JD). Derived from 'DATE_OBS'.</description></column>

    <column name="tracked" type="bool" unit="" ucd=""><description>to add</description></column>
    <column name="short" type="bool" unit="" ucd=""><description>to add</description></column>
    <column name="astrometry" type="bool" unit="" ucd=""><description>to add</description></column>

    <column name="light" type="bigint" unit="" ucd="meta.id" required="True"><description>to add</description></column>
    <column name="master_flat" type="bigint" unit="" ucd="meta.id" required="True"><description>to add</description></column>
    <column name="master_dark" type="bigint" unit="" ucd="meta.id" required="True"><description>to add</description></column>
    <column name="master_bias" type="bigint" unit="" ucd="meta.id" required="True"><description>to add</description></column>

    <!-- Headers here ... -->
  </table>

  <table id="reduced" onDisk="True" adql="True" mixin="//scs#pgs-pos-index">
    <column name="id" type="bigint" unit="" ucd="meta.id;meta.main" required="True">
      <description>Database identifier of the file.</description></column>

    <column name="filetype" type="text" unit="" ucd="" required="True"><description>to add</description></column>
    <column name="filename" type="text" unit="" ucd="meta.id;meta.file"><description></description></column>
  </table>

  <!-- Do we need the mixin for this? -->
  <table id="composition" onDisk="True" adql="True" mixin="//scs#pgs-pos-index">
    <column name="reduced" type="bigint" unit="" ucd="meta.id"><description>to add</description></column>
    <column name="raw" type="bigint" unit="" ucd="meta.id"><description>to add</description></column>
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
    <make table="all"/>
    <make table="reduced"/>
    <make table="composition"/>
  </data>

</resource>

