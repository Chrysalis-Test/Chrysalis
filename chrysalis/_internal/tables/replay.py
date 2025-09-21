import pickle
from typing import Any

import duckdb

from chrysalis._internal.tables.relation import KnowledgeBase


def get_transformed_input(
    applied_transform_id: str,
    input_data_id: str,
    knowledge_base: KnowledgeBase,
    conn: duckdb.DuckDBPyConnection,
) -> Any:
    match conn.execute(
        """
SELECT obj
FROM input_data
WHERE id = ?;
    """,
        (input_data_id,),
    ).fetchone():
        case None:
            raise RuntimeError(f"No input data obj exists with id: `{input_data_id}`.")
        case (input_data_blob,):
            input_data = pickle.loads(input_data_blob)
            pass
        case _:
            raise RuntimeError(
                f"An error was encountered while attempting to fetch input data obj: `{input_data_id}`."
            )

    relation_chain = conn.execute(
        """
WITH relation_chain AS (
    SELECT
        relation_chain_id AS id
    FROM
        applied_transformation
    WHERE
        applied_transformation.id = ?
)
SELECT
    t.id
FROM
    applied_transformation a
INNER JOIN
    relation_chain rc
ON
    a.relation_chain_id = rc.id
INNER JOIN
    transformation t
ON
    t.id = a.transformation
ORDER BY
    link_index;
""",
        (applied_transform_id,),
    ).fetchall()

    for (transform_id,) in relation_chain:
        input_data = knowledge_base.relations[transform_id].apply_transform(input_data)

    return input_data
