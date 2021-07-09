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

cone_service_meta_elems = [
    MetaElem(name="title", text="Observations cone search"),
    MetaElem(name="shortName", text="Obs Cone"),
    MetaElem(name="testQuery.ra", text="51"),
    MetaElem(name="testQuery.dec", text="0"),
    MetaElem(name="testQuery.sr", text="0.01"),
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

    # Make the composition table

    # Create the cone service element
    # (disabled for the moment)
    # service = SubElement(top, "service", id="cone", allowed="scs.xml,form")
    # for elem in cone_service_meta_elems:
    #     meta = SubElement(service, "meta", name=elem.name)
    #     meta.text = elem.text

    # core = SubElement(service, "scsCore", queriedTable=table_id)
    # SubElement(core, "FEED", source="//scs#coreDescs")

    # Create the data element
    data = SubElement(top, "data", id="d", updating="True")
    SubElement(data, "publish", sets="local")
    for table_id in table_ids + ["composition"]:
        SubElement(data, "make", table=table_id)

    return top


def make_composition_table(parent):
    table_id = "components"

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
        name="master",
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
        name="raw",
        type="bigint",
        unit="",
        ucd="meta.id",
        required="True",
    )
    descr = SubElement(col, "description")
    descr.text = "Reference to the identifier of the raw file"


def make_table_element(parent, table_id, headers_file, specific_columns=None):
    table = SubElement(
        parent,
        "table",
        id=table_id,
        onDisk="True",
        adql="True",
        mixin="//scs#pgs-pos-index",
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


def to_column(parent, dictionary):
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


def prettify(elem):
    """Return a pretty-printed XML string for the Element."""
    rough_string = tostring(elem, "utf-8")
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")
