
-- High level information about the observations
-- Maybe needs a better name than 'all' --> overview ?
CREATE TABLE observations.all (
        id SERIAL PRIMARY KEY,
        
        -- Convenience Columns
        obs_jd FLOAT8,  -- Julian Date of obervation
        dec    FLOAT8,  -- degrees
        ra     FLOAT8,  -- degrees

        -- Other columns indicating the filetype ?
        tracked    BOOL, -- used the tracking
        short      BOOL, -- short exposure
        astrometry BOOL, -- astrometry info available
        
        -- Links to the reduced images in observations.reduced
        light INTEGER UNIQUE NOT NULL, -- ref: observations.reduced
        -- Maybe remove the 'master_' prefix, as it is already implied?
        master_flat INTEGER NOT NULL, -- ref: observations.reduced
        master_dark INTEGER NOT NULL, -- ref: observations.reduced
        master_bias INTEGER NOT NULL, -- ref: observations.reduced

        -- Other (header) information;
        FILTER TEXT,
        ...
);

CREATE TABLE observations.reduced (
        id SERIAL PRIMARY KEY,
        -- L, F, D, B (could be an enum type)
        -- or maybe LIGHT/IMAG, FLAT, DARK, BIAS
        filetype CHAR(1) NOT NULL, 
        filename TEXT NOT NULL,

        -- All the header keywords
        ...
);

-- Question: how to indicate the relationship between master files
-- flats <-- dark <-- bias

-- Table indicating the composition relationship of master files
-- i.e. which raw files where used to create this file.
CREATE TABLE observations.composition (
        reduced INTEGER, -- Maybe name it 'master' ref: observations.reduced
        raw INTEGER, -- ref: observations.raw
        PRIMARY KEY (master, raw) -- many-many relation
);

CREATE TABLE observations.raw (
        -- Same as before
);
