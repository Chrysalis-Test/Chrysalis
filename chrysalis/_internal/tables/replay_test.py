import ast
import pickle

import duckdb

from chrysalis._internal.tables.replay import get_transformed_input
from chrysalis._internal.tables.relation import KnowledgeBase, generate_uuid
from chrysalis._internal.tables.defs import (
    TemporarySqlite3RelationConnection,
    sqlite_to_duckdb,
)


def _insert_input_data(
    obj: ast.Expression,
    conn: duckdb.DuckDBPyConnection,
) -> str:
    """Insert a record into the `input_data` table."""
    input_data_id = generate_uuid()
    conn.execute(
        """
INSERT INTO input_data (id, obj)
VALUES (?, ?);
""",
        (input_data_id, pickle.dumps(obj)),
    )
    return input_data_id


def _insert_applied_transformation(
    transformation: str,
    relation_chain_id: str,
    link_index: int,
    conn: duckdb.DuckDBPyConnection,
) -> str:
    """Insert a record into the `applied_transformation` table."""
    applied_transformation_id = generate_uuid()
    conn.execute(
        """
INSERT INTO applied_transformation
(id, transformation, relation_chain_id, link_index)
VALUES
(?, ?, ?, ?);
""",
        (
            applied_transformation_id,
            transformation,
            relation_chain_id,
            link_index,
        ),
    )
    return applied_transformation_id


def test_transformed_input(
    sample_expression_1: ast.Expression,
    mock_knowledge_base: KnowledgeBase,
) -> None:
    with TemporarySqlite3RelationConnection(mock_knowledge_base) as (
        sqlite_conn,
        db_path,
    ):
        sqlite_conn.commit()
        conn = sqlite_to_duckdb(db_path)

    relation_chain_id = generate_uuid()

    input_data_id = _insert_input_data(sample_expression_1, conn)
    _ = _insert_applied_transformation(
        transformation=mock_knowledge_base._transformations["inverse"],
        relation_chain_id=relation_chain_id,
        link_index=0,
        conn=conn,
    )
    applied_transform_id = _insert_applied_transformation(
        transformation=mock_knowledge_base._transformations["add_1_to_expression"],
        relation_chain_id=relation_chain_id,
        link_index=0,
        conn=conn,
    )

    transformed_input = get_transformed_input(
        applied_transform_id=applied_transform_id,
        input_data_id=input_data_id,
        knowledge_base=mock_knowledge_base,
        conn=conn,
    )

    assert ast.unparse(transformed_input) == "-1 * (3 - 2 + 4 / 2 + 1) + 1"
