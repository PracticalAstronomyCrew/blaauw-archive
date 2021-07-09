from columns import read_columns

# Map python types to SQL types
type_map = {
    "int": "INTEGER",
    "float": "FLOAT8",
    "bool": "BOOL",
    "str": "TEXT",
}

unique_columns = {"filename", "file_id"}
col_fmt = "    {0} {1}{2},\n"


def gen_sql(schema, col_file):
    result = ""
    result += """
-- Reset first
DROP SCHEMA  IF EXISTS {schema} CASCADE;

CREATE SCHEMA {schema};
"""
    # Make the raw table
    result += "CREATE TABLE {schema}.raw (\n"
    result += "    id SERIAL PRIMARY KEY,  -- Identifier\n"

    result += csv_to_columns("definitions/columns/raw.csv")
    result += csv_to_columns(col_file, last_line=True)

    result += "\n);\n\n"

    # Make the reduced table
    result += "CREATE TABLE {schema}.reduced (\n"
    result += "    id SERIAL PRIMARY KEY,  -- Identifier\n"
    result += csv_to_columns("definitions/columns/reduced.csv")
    result += csv_to_columns(col_file, last_line=True)
    result += "\n);\n\n"

    # Make the all table
    result += "CREATE TABLE {schema}.calibration (\n"
    result += "    id SERIAL PRIMARY KEY,  -- Identifier\n"
    result += csv_to_columns("definitions/columns/calibration.csv")
    result += csv_to_columns(col_file, last_line=True)
    result += "\n);\n\n"

    # Make the composition table
    result += """

CREATE TABLE observations.components (
        master INTEGER, 
        raw INTEGER,
        PRIMARY KEY (master, raw)
);

    """
    result += """
GRANT ALL PRIVILEGES ON SCHEMA {schema} TO dachsroot WITH GRANT OPTION;
GRANT SELECT ON {schema}.raw TO dachsroot WITH GRANT OPTION;
GRANT SELECT ON {schema}.reduced TO dachsroot WITH GRANT OPTION;
GRANT SELECT ON {schema}.calibration TO dachsroot WITH GRANT OPTION;
GRANT SELECT ON {schema}.components TO dachsroot WITH GRANT OPTION;
"""

    return result.format(schema=schema)


def csv_to_columns(col_file, last_line=False):
    result = ""
    lines = read_columns(col_file)
    for col in lines:
        result += col_fmt.format(
            col["name"],
            type_map[col["type"]],
            " UNIQUE" if col["name"] in unique_columns else "",
        )
    if last_line:
        result = result[:-2]  # remove comma of the last column item
    return result
