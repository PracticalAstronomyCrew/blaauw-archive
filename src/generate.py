#!/usr/bin/env python3
from rd_xml import gen_xml, prettify
from table_sql import gen_sql
import sys

# File defaults (w.r.t project root)
col_file_default = "definitions/column-list.csv"
doc_file_default = "definitions/doc.rst"

rd_dest_default = "generated/q.rd"
table_dest_default = "generated/table.sql"


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
    rd_tree = gen_xml("observations", "raw", col_file, doc_file)
    print("Saving to", rd_dest)
    with open(rd_dest, "w") as f:
        f.write(prettify(rd_tree))

    # Generate the SQL table definition
    table_str = gen_sql("observations", "raw", col_file)
    with open(table_dest, "w") as f:
        f.write(table_str)


if __name__ == "__main__":
    main()
