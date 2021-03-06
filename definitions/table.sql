-- Reset first
DROP SCHEMA  IF EXISTS observations CASCADE;

CREATE SCHEMA observations;

CREATE TABLE observations.raw (
	id SERIAL PRIMARY KEY,  -- Identifier

	-- Computed columns
	obs_jd   FLOAT8,
	dec      FLOAT8,  -- degrees
	ra       FLOAT8,   -- degrees
	filename TEXT UNIQUE,

	-- Direct FITS Headers
	SIMPLE      BOOL,
	BITPIX      INTEGER,
	NAXIS       INTEGER,
	NAXIS1      INTEGER,
	NAXIS2      INTEGER,
	BSCALE      FLOAT8,
	BZERO       FLOAT8,
	BIAS        INTEGER,
	FOCALLEN    FLOAT8,
	APTAREA     FLOAT8,
	APTDIA      FLOAT8,
	DATE_OBS    TEXT UNIQUE,
	TIME_OBS    TEXT,
	SWCREATE    TEXT,
	SET_TEMP    FLOAT8,
	COLORCCD    INTEGER,
	DISPCOLR    INTEGER,
	IMAGETYP    TEXT,
	CCDSFPT     INTEGER,
	XORGSUBF    INTEGER,
	YORGSUBF    INTEGER,
	CCDSUBFL    INTEGER,
	CCDSUBFT    INTEGER,
	XBINNING    INTEGER,
	CCDXBIN     INTEGER,
	YBINNING    INTEGER,
	CCDYBIN     INTEGER,
	EXPSTATE    INTEGER,
	CCD_TEMP    FLOAT8,
	TEMPERAT    FLOAT8,
	OBJECT      TEXT,
	OBJCTRA     TEXT,
	OBJCTDEC    TEXT,
	TELTKRA     FLOAT8,
	TELTKDEC    FLOAT8,
	CENTAZ      FLOAT8,
	CENTALT     FLOAT8,
	TELHA       TEXT,
	LST         TEXT,
	AIRMASS     FLOAT8,
	SITELAT     TEXT,
	SITELONG    TEXT,
	INSTRUME    TEXT,
	EGAIN       FLOAT8,
	E_GAIN      FLOAT8,
	XPIXSZ      FLOAT8,
	YPIXSZ      FLOAT8,
	SBIGIMG     INTEGER,
	USER_2      TEXT,
	DATAMAX     INTEGER,
	SBSTDVER    TEXT,
	FILTER      TEXT,
	EXPTIME     FLOAT8,
	EXPOSURE    FLOAT8,
	CBLACK      INTEGER,
	CWHITE      INTEGER,
	CTYPE1      TEXT,
	CTYPE2      TEXT,
	EQUINOX     FLOAT8,
	CRVAL1      FLOAT8,
	CRVAL2      FLOAT8,
	CRPIX1      FLOAT8,
	CRPIX2      FLOAT8,
	CUNIT1      TEXT,
	CUNIT2      TEXT,
	CD1_1       FLOAT8,
	CD1_2       FLOAT8,
	CD2_1       FLOAT8,
	CD2_2       FLOAT8,
	PLATE_SCALE FLOAT8 -- technically not a direct header.
);

GRANT ALL PRIVILEGES ON SCHEMA observations TO gavoadmin WITH GRANT OPTION;
GRANT SELECT ON observations.raw TO gavoadmin WITH GRANT OPTION;
