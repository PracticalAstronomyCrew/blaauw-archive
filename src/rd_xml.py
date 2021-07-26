#!/usr/bin/env python3
from xml.etree.ElementTree import tostring, Element, SubElement, Comment
from xml.dom import minidom
from collections import namedtuple
from datetime import date

from columns import read_columns


MetaElem = namedtuple("MetaElem", "name text")

# TODO: Move to another file, maybe csv as well
resource_meta_elems = [
    MetaElem("title", "Raw Observation Data"),
    # Maybe creation date is the date of the release? Not the update
    MetaElem("creationDate", date.today().isoformat()),
    MetaElem(
        "description",
        "This database contains the header information of"
        "the raw observations made in the Blaauw Observatory. It is "
        "currently in heavy development!",
    ),
    # Add a proper name, not mine ;)
    MetaElem("creator", "Sten Sipma"),
    MetaElem("subject", "Raw Observations"),
    MetaElem("subject", "Bias Frames"),
    MetaElem("subject", "Dark Frames"),
    MetaElem("subject", "Flat Frames"),
    MetaElem("subject", "Target Frames"),
    MetaElem("subject", "FITS Headers"),
    MetaElem("type", "Archive"),
]

# Map python types to types in the resource descriptor
type_map = {
    "int": "bigint",
    "float": "double precision",
    "bool": "bigint",
    "str": "text",
}


def gen_xml(schema, headers_file, doc_file):
    top = Element("resource", schema=schema)

    # Insert meta headers
    for elem in resource_meta_elems:
        meta = SubElement(top, "meta", name=elem.name)
        meta.text = elem.text

    # Insert the documentation
    with open(doc_file, "r") as f:
        longdoc_text = f.read()
    longdoc = SubElement(top, "meta", name="_longdoc", format="rst")
    longdoc.text = longdoc_text

    # Make the tables which include headers
    table_ids = ["raw", "calibration", "reduced"]
    for table_id in table_ids:
        make_table_element(
            top,
            table_id=table_id,
            headers_file=headers_file,
            specific_columns="definitions/columns/" + table_id + ".csv",
        )

    # And the table with the relations between raw and reduced files
    make_composition_table(top)

    # Create the cone service elements
    # For the "raw" table
    service = SubElement(top, "service", id="cone", allowed="scs.xml,form")
    SubElement(
        service, "meta", name="title", text="Raw Observations Cone Search"
    )
    SubElement(service, "meta", name="shortname", text="Cone Raw")
    core = SubElement(service, "scsCore", queriedTable="raw")
    SubElement(core, "FEED", source="//scs#coreDescs")

    # For the "reduced" table
    service = SubElement(top, "service", id="cone", allowed="scs.xml,form")
    SubElement(
        service, "meta", name="title", text="Reduced Observations Cone Search"
    )
    SubElement(service, "meta", name="shortname", text="Cone Red")
    core = SubElement(service, "scsCore", queriedTable="reduced")
    SubElement(core, "FEED", source="//scs#coreDescs")

    # Create the data element
    data = SubElement(top, "data", id="d", updating="True")
    SubElement(data, "publish", sets="local")
    for table_id in table_ids + ["composition"]:
        SubElement(data, "make", table=table_id)

    return top


def make_composition_table(parent):
    table_id = "composition"

    # Make the composition table
    table = SubElement(
        parent,
        "table",
        id=table_id,
        onDisk="True",
        adql="True",
    )

    col = SubElement(
        table,
        "column",
        name="master_id",
        type="bigint",
        unit="",
        ucd="meta.id",
        required="True",
    )
    descr = SubElement(col, "description")
    descr.text = "Reference to the identifier of the calibration"

    col = SubElement(
        table,
        "column",
        name="raw_id",
        type="bigint",
        unit="",
        ucd="meta.id",
        required="True",
    )
    descr = SubElement(col, "description")
    descr.text = "Reference to the identifier of the raw file"

    # Add the foreign key elements
    SubElement(
        table,
        "foreignKey",
        dest="id",
        inTable="calibration",
        source="master_id",
    )
    SubElement(table, "foreignKey", dest="id", inTable="raw", source="raw_id")


def make_table_element(parent, table_id, headers_file, specific_columns=None):
    # Only apply mixin for tables containing coordinates (i.e. not the calibration table)
    if table_id != "calibration":
        table = SubElement(
            parent,
            "table",
            id=table_id,
            onDisk="True",
            adql="True",
            mixin="//scs#pgs-pos-index",
        )
    else:
        table = SubElement(
            parent,
            "table",
            id=table_id,
            onDisk="True",
            adql="True",
        )

    # Create the identifier column
    col = SubElement(
        table,
        "column",
        name="id",
        type="bigint",
        unit="",
        ucd="meta.id;meta.main",
        required="True",
    )
    descr = SubElement(col, "description")
    descr.text = "Database identifier of the file."

    # Add the columns specific to this table
    if specific_columns is not None:
        columns = read_columns(specific_columns)
        for col in columns:
            to_column(table, col)

    # Add the general header keywords
    columns = read_columns(headers_file)
    for col in columns:
        to_column(table, col)


def to_column(parent, dictionary: dict):
    """Convert a dictionary to a SubElement column object attached to `parent`"""
    d = dictionary

    col = SubElement(
        parent,
        "column",
        name=d["name"],
        type=type_map[d["type"]],
        unit=d["unit"],
        ucd=d["ucd"],
    )

    description = d["description"]
    if len(description) < 1:
        description = "No Description (TODO)"

    descr = SubElement(col, "description")
    descr.text = description

    # The column is also a foreign key
    if len(d["fk-table"]) > 0 and len(d["fk-column"]) > 0:
        SubElement(
            parent,
            "foreignKey",
            dest=d["fk-column"],
            inTable=d["fk-table"],
            source=d["name"],
        )


def prettify(elem):
    """Return a pretty-printed XML string for the Element."""
    rough_string = tostring(elem, "utf-8")
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")
