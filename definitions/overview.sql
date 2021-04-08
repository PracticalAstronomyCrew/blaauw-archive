-- General resetting etc.
DROP SCHEMA  IF EXISTS observations CASCADE;
CREATE SCHEMA observations;

CREATE TABLE observations.calibrations (
        id SERIAL PRIMARY KEY,
        obs_jd FLOAT8,

        /* header information */
);

CREATE TABLE observations.reduced (
        id SERIAL PRIMARY KEY,
        
        -- Convenience Columns
        obs_jd FLOAT8,  -- Julian Date of obervation
        dec    FLOAT8,  -- degrees
        ra     FLOAT8,  -- degrees

        tracked    BOOL, -- used the tracking
        short      BOOL, -- short exposure
        astrometry BOOL, -- astrometry info available
        telescope TEXT,
        
        -- Links to the reduced images in observations.reduced
        raw INTEGER UNIQUE NOT NULL, -- ref: observations.raw
        -- Maybe remove the 'master_' prefix, as it is already implied?
        master_flat INTEGER NOT NULL, -- ref: observations.calibrations
        master_dark INTEGER NOT NULL, -- ref: observations.calibrations
        master_bias INTEGER NOT NULL, -- ref: observations.calibrations

        /* header information */
);

-- Indicates which raw files where used to create a given calibration file
CREATE TABLE observations.components (
        master INTEGER, -- ref: observations.calibration
        raw INTEGER,    -- ref: observations.raw
        PRIMARY KEY (master, raw)
);

CREATE TABLE observations.raw (
        -- Same as before
);


-- Permissions
GRANT ALL PRIVILEGES ON SCHEMA observations TO gavoadmin WITH GRANT OPTION;
GRANT SELECT ON observations.raw         TO gavoadmin WITH GRANT OPTION;
GRANT SELECT ON observations.components  TO gavoadmin WITH GRANT OPTION;
GRANT SELECT ON observations.reduced     TO gavoadmin WITH GRANT OPTION;
GRANT SELECT ON observations.calibration TO gavoadmin WITH GRANT OPTION;
