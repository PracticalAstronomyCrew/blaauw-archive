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


def gen_sql(schema, table, col_file):
    result = ""
    result += """
-- Reset first
DROP SCHEMA  IF EXISTS {schema} CASCADE;

CREATE SCHEMA {schema};
"""
    result += "CREATE TABLE observations.raw (\n"
    result += "    id SERIAL PRIMARY KEY,  -- Identifier\n"
    lines = read_columns(col_file)
    for col in lines:
        result += col_fmt.format(
            col["name"],
            type_map[col["type"]],
            " UNIQUE" if col["name"] in unique_columns else "",
        )
    result = result[:-2]  # remove comma of the last column item
    result += "\n);\n\n"
    result += """
GRANT ALL PRIVILEGES ON SCHEMA {schema} TO feed WITH GRANT OPTION;
GRANT SELECT ON {schema}.{table} TO feed WITH GRANT OPTION;
"""

    return result.format(schema=schema, table=table)
