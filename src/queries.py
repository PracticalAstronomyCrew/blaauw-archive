from __future__ import annotations
from pypika import Table, Query, Parameter


def make_insert_query(columns: list[dict], table_name="raw") -> Query:
    raw = Table("observations.{}".format(table_name))

    q = (
        Query.into(raw)
        .columns(*(col["name"] for col in columns))
        .insert(*(Parameter("%({})s".format(col["py-name"])) for col in columns))
    )
    return q


def make_update_query(header: dict, columns: list[dict], table_name="raw") -> Query:
    raw = Table("observations.{}".format(table_name))

    q = Query.update(raw)
    for col in columns:
        if col["py-name"] in header:
            q = q.set(col["name"], Parameter("%({})s".format(col["py-name"])))
    q = q.where(raw.file_id == Parameter("%({})s".format("file_id")))
    return q


if __name__ == "__main__":
    from columns import combine_tables

    raw_file = "./definitions/columns/raw.csv"
    head_file = "./definitions/columns/headers.csv"
    columns = combine_tables([raw_file, head_file])

    q = make_update_query({"FILENAME": 1, "obs_jd": 3}, columns)

    print(q.get_sql())
