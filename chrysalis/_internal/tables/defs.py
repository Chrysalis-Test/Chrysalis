import sqlite3
from pathlib import Path
from tempfile import TemporaryDirectory

import duckdb

from chrysalis._internal.tables.relation import KnowledgeBase

_CREATE_TRANSFORMATION_TABLE = """
CREATE TABLE transformation (
    id TEXT PRIMARY KEY,
    name TEXT UNIQUE NOT NULL
);
"""

_CREATE_INVARIANT_TABLE = """
CREATE TABLE invariant (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL
);
"""

_CREATE_RELATION_TABLE = """
CREATE TABLE relation (
    transformation TEXT NOT NULL,
    invariant TEXT NOT NULL,

    FOREIGN KEY (transformation) REFERENCES transformation(id),
    FOREIGN KEY (invariant) REFERENCES invariant(id)
);
"""

_CREATE_INPUT_DATA_TABLE = """
CREATE TABLE input_data (
    id TEXT PRIMARY KEY,
    obj BLOB NOT NULL
);
"""

_CREATE_APPLIED_TRANSFORMATION_TABLE = """
CREATE TABLE applied_transformation (
    id TEXT PRIMARY KEY,
    transformation TEXT NOT NULL,
    relation_chain_id TEXT NOT NULL,
    link_index INT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (transformation) REFERENCES transformation(id)
);
"""

_CREATE_FAILED_INVARIANT_TABLE = """
CREATE TABLE failed_invariant (
    id TEXT PRIMARY KEY,
    invariant TEXT NOT NULL,
    applied_transformation TEXT NOT NULL,
    input_data TEXT NOT NULL,

    FOREIGN KEY (invariant) REFERENCES invariant(id),
    FOREIGN KEY (applied_transformation) REFERENCES applied_transformation(id),
    FOREIGN KEY (input_data) REFERENCES input_data(id)
);
"""


class TemporarySqlite3RelationConnection(TemporaryDirectory):
    """
    A temporary sqlite3 database designed to be used for transactional inserts.

    During metamorphic testing, we want to record the order of which transformations are
    applied and the result of each invariant tested in a relation chain. This data is
    available after each step that is executed in the engine. By definition, this
    pattern follows the transactional processing pattern and thus justifies using
    sqlite3.

    This database maintains two tables that are required to store the results of
    execution of a relation chain. The first table is the `transformation` table which
    records the order of which tranformations are applied to input data. The second
    table `failed_invariant` represents the result of a individual invariant tested for
    a given transformation that failed. It is important to note, it is possible that
    multiple invariants apply to the same transformation and thus a single transformation
    can have multiple invariants that fail.

    Given this database design, it is not required to store the result of
    transformations on the input data. Instead, the transformations can be reapplied to
    the input data to acheive indiviudal instances of transformed data that is
    requested. This dramatically reduces the amount of data that is required to be
    stored.

    Since this is a temporary sqlite3 connection, it is expected that all data will be
    extracted before exiting the context manager.
    """

    def __init__(self, knowledge_base: KnowledgeBase):
        self._knowledge_base = knowledge_base
        super().__init__()

    def __enter__(self, *args, **kwargs) -> tuple[sqlite3.Connection, Path]:
        """
        Create a database in the temporary directory created during initialization.

        In addition to creating the database, configure the sqlite3 database rules and
        create the relevant tables.
        """
        temp_dir = super().__enter__(*args, **kwargs)
        # Arguably, this context manager should be based off `TemporaryFile` instead of
        # `TemporaryDirectory`, but this design was chosen due to ease of
        # implementation.
        self._db_path = Path(temp_dir) / "chry.db"
        self._conn = sqlite3.connect(self._db_path)

        # Sqlite3 doesn't enfore foreign key existance by default.
        self._conn.execute("PRAGMA foreign_keys = ON")

        self._conn.execute(_CREATE_TRANSFORMATION_TABLE)
        self._conn.execute(_CREATE_INVARIANT_TABLE)
        self._conn.execute(_CREATE_RELATION_TABLE)
        self._conn.execute(_CREATE_INPUT_DATA_TABLE)
        self._conn.execute(_CREATE_APPLIED_TRANSFORMATION_TABLE)
        self._conn.execute(_CREATE_FAILED_INVARIANT_TABLE)

        for (
            transformation_name,
            transformation_id,
        ) in self._knowledge_base.transformation_ids.items():
            self._conn.execute(
                "INSERT INTO transformation (id, name) VALUES (?, ?);",
                (transformation_id, transformation_name),
            )

        for (
            invariant_name,
            invariant_id,
        ) in self._knowledge_base.invariant_ids.items():
            self._conn.execute(
                "INSERT INTO invariant (id, name) VALUES (?, ?);",
                (invariant_id, invariant_name),
            )

        for relation in self._knowledge_base.relations.values():
            for invariant_id in relation.invariants:
                self._conn.execute(
                    "INSERT INTO relation (transformation, invariant) VALUES (?, ?);",
                    (relation.transformation_id, invariant_id),
                )

        return self._conn, self._db_path

    def __exit__(self, *args, **kwargs):
        self._conn.close()
        return super().__exit__(*args, **kwargs)


def init_duckdb(conn: duckdb.DuckDBPyConnection) -> None:
    conn.execute(_CREATE_TRANSFORMATION_TABLE)
    conn.execute(_CREATE_INVARIANT_TABLE)
    conn.execute(_CREATE_RELATION_TABLE)
    conn.execute(_CREATE_INPUT_DATA_TABLE)
    conn.execute(_CREATE_APPLIED_TRANSFORMATION_TABLE)
    conn.execute(_CREATE_FAILED_INVARIANT_TABLE)


def sqlite_to_duckdb(
    sqlite_db: Path,
    output_db_path: Path | None = None,
) -> duckdb.DuckDBPyConnection:
    """
    Convert a chrysalis sqlite3 database into a duckdb database.

    Converting a sqilte3 database to a duckdb database is non-trivial due to the
    conversion needing to be done one table at a time. Additionally, some tables, such
    as the `applied_transformation` table require additional care as self-referential
    foreign key constraints can become problematic.
    """
    if output_db_path is not None:
        duckdb_conn = duckdb.connect(output_db_path)
    else:
        duckdb_conn = duckdb.connect()

    # The schema of the tables needs to be specified before records are inserted. If
    # the schema is inferred from sqlite, it may be wrong.
    init_duckdb(duckdb_conn)

    # Sqlite needs to be installed within duckdb before `sqlite_scan` can be used.
    duckdb_conn.execute("INSTALL sqlite;")

    duckdb_conn.execute(
        """
INSERT INTO transformation
SELECT * FROM sqlite_scan(?, ?);
                """,
        (str(sqlite_db), "transformation"),
    )

    duckdb_conn.execute(
        """
INSERT INTO invariant
SELECT * FROM sqlite_scan(?, ?);
                """,
        (str(sqlite_db), "invariant"),
    )

    duckdb_conn.execute(
        """
INSERT INTO relation
SELECT * FROM sqlite_scan(?, ?);
                """,
        (str(sqlite_db), "relation"),
    )

    duckdb_conn.execute(
        """
INSERT INTO input_data
SELECT * FROM sqlite_scan(?, ?);
                """,
        (str(sqlite_db), "input_data"),
    )

    duckdb_conn.execute(
        """
INSERT INTO applied_transformation
SELECT * FROM sqlite_scan(?, ?);
                """,
        (str(sqlite_db), "applied_transformation"),
    )

    duckdb_conn.execute(
        """
INSERT INTO failed_invariant
SELECT * FROM sqlite_scan(?, ?);
                """,
        (str(sqlite_db), "failed_invariant"),
    )
    return duckdb_conn
