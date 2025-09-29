import ast
import pickle
from typing import Generator

from unittest.mock import MagicMock

from chrysalis._internal.engine import Engine
from chrysalis._internal.tables.relation import KnowledgeBase, Relation
from chrysalis._internal.tables.defs import TemporarySqlite3RelationConnection
from chrysalis._internal.conftest import eval_expr


def mock_generator(relations: list[Relation]) -> Generator[Relation, None, None]:
    def generator() -> Generator[Relation, None, None]:
        for relation in relations:
            yield relation

    return generator()


def test_successful_relation_chain(
    sample_expression_1: ast.Expression,
    correct_relation_chain: list[Relation[ast.Expression, float]],
    mock_knowledge_base: KnowledgeBase,
) -> None:
    with TemporarySqlite3RelationConnection(knowledge_base=mock_knowledge_base) as (
        temp_conn,
        db_path,
    ):
        search_space = MagicMock()
        search_space.create_generator.return_value = mock_generator(
            correct_relation_chain
        )

        engine = Engine(
            sut=eval_expr,
            input_data=[sample_expression_1],
            search_space=search_space,
            sqlite_conn=temp_conn,
            sqlite_db=db_path,
        )
        engine.execute(chain_length=3, num_chains=1)
        conn = engine.results_to_duckdb()

    match conn.execute("SELECT * FROM input_data;").fetchall():
        case ((_, obj),):
            assert ast.unparse(pickle.loads(obj)) == ast.unparse(sample_expression_1)
        case _:
            raise ValueError(
                "Error extracting sample expression from returned duckdb connection."
            )

    assert [
        ("identity", 0),
        ("inverse", 1),
        ("add_1_to_expression", 2),
    ] == conn.execute(
        """
SELECT trans.name, appl_trans.link_index
FROM applied_transformation appl_trans
INNER JOIN transformation trans ON appl_trans.transformation = trans.id
ORDER BY appl_trans.link_index;
                 """
    ).fetchall()

    assert conn.execute("SELECT COUNT(*) FROM failed_invariant").fetchall() == [(0,)]


def test_unsuccessful_relation_chain(
    sample_expression_1: ast.Expression,
    incorrect_relation_chain: list[Relation[ast.Expression, float]],
    mock_knowledge_base: KnowledgeBase,
) -> None:
    with TemporarySqlite3RelationConnection(knowledge_base=mock_knowledge_base) as (
        temp_conn,
        db_path,
    ):
        search_space = MagicMock()
        search_space.create_generator.return_value = mock_generator(
            incorrect_relation_chain
        )
        engine = Engine(
            sut=eval_expr,
            input_data=[sample_expression_1],
            search_space=search_space,
            sqlite_conn=temp_conn,
            sqlite_db=db_path,
        )
        engine.execute(chain_length=3, num_chains=1)
        conn = engine.results_to_duckdb()

    match conn.execute("SELECT * FROM input_data;").fetchall():
        case ((_, obj),):
            assert ast.unparse(pickle.loads(obj)) == ast.unparse(sample_expression_1)
        case _:
            raise ValueError(
                "Error extracting sample expression from returned duckdb connection."
            )

    assert [
        ("identity", 0),
        ("inverse", 1),
        ("subtract_1_from_expression", 2),
    ] == conn.execute(
        """
SELECT trans.name, appl_trans.link_index
FROM applied_transformation appl_trans
INNER JOIN transformation trans ON appl_trans.transformation = trans.id
ORDER BY appl_trans.link_index;
                 """
    ).fetchall()

    assert [("equals",)] == conn.execute(
        """
SELECT inv.name
FROM failed_invariant f_inv
INNER JOIN invariant inv ON f_inv.invariant = inv.id;
"""
    ).fetchall()
