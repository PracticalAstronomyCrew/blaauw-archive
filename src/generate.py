#!/usr/bin/env python3
from rd_xml import gen_xml, prettify
from table_sql import gen_sql
import sys

# File defaults (w.r.t project root)
col_file_default = "definitions/columns/headers.csv"
doc_file_default = "definitions/doc.rst"

rd_dest_default = "generated/q.rd"
table_dest_default = "generated/table.sql"

modeline = """<!--
vim: ft=xml
vim:et:sta:sw=2
-->
"""


def main():
    if len(sys.argv) == 1:
        col_file = col_file_default
        doc_file = doc_file_default
        rd_dest = rd_dest_default
        table_dest = table_dest_default
    elif len(sys.argv) == 5:
        col_file, doc_file, rd_dest, table_dest = sys.argv[1:]
    else:
        print("Invalid arguments. Either give none or use:")
        print(
            "$ ./generate.py [columns file] [documentation file]"
            " [rd destination] [table destination]"
        )
        exit(-1)

    # Generate the XML resource description
    rd_tree = gen_xml(
        "observations",
        col_file,
        doc_file,
    )

    print("Saving RD to", rd_dest)
    xml_str = prettify(rd_tree)
    with open(rd_dest, "w") as f:
        # Write the xml tree
        f.write(xml_str)
        # Add the modeline, to let Vim know that this is an xml file
        f.write(modeline)

    # Generate the SQL table definition
    table_str = gen_sql("observations", col_file)
    print("Saving SQL tables to", table_dest)
    with open(table_dest, "w") as f:
        f.write(table_str)


if __name__ == "__main__":
    main()
