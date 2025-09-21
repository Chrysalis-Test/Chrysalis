import ast

import pytest
import duckdb

from chrysalis._internal import invariants
from chrysalis._internal.tables.relation import KnowledgeBase
from chrysalis._internal.tables.defs import init_duckdb
from chrysalis._internal.conftest import identity


def test_create_relation() -> None:
    knowledge_base = KnowledgeBase[ast.Expression, float]()
    knowledge_base.register(
        transformation=identity,
        invariant=invariants.equals,
    )

    assert len(knowledge_base.relations) == 1
    relation = next(iter(knowledge_base.relations.values()))
    assert relation.transformation_name == "identity"
    assert [invariant.__name__ for invariant in relation.invariants.values()] == [
        "equals"
    ]


def test_create_relation_lambda() -> None:
    knowledge_base = KnowledgeBase[int, int]()
    with pytest.raises(
        ValueError,
        match="Lambda functions cannot be used as transformation or invariants.",
    ):
        knowledge_base.register(
            transformation=lambda x: x,
            invariant=lambda x, y: x == y,
        )


def test_load_prev_knowledge_base(mock_knowledge_base: KnowledgeBase) -> None:
    conn = duckdb.connect()
    init_duckdb(conn)

    conn.executemany(
        "INSERT INTO transformation (id, name) VALUES (?, ?);",
        [
            ("1", "identity"),
            ("2", "inverse"),
            ("3", "add_1_to_expression"),
        ],
    )

    conn.executemany(
        "INSERT INTO invariant (id, name) VALUES (?, ?);",
        [
            ("a", "equals"),
            ("b", "not_same_sign"),
            ("c", "greater_than"),
        ],
    )

    conn.executemany(
        "INSERT INTO relation (transformation, invariant) VALUES (?, ?);",
        [
            ("1", "a"),
            ("2", "b"),
            ("3", "c"),
        ],
    )

    kb = KnowledgeBase.load_previous(current=mock_knowledge_base, conn=conn)

    assert kb._transformations == {
        "identity": "1",
        "inverse": "2",
        "add_1_to_expression": "3",
    }
    assert kb._invariants == {
        "equals": "a",
        "not_same_sign": "b",
        "greater_than": "c",
    }

    assert list(kb._relations["1"]._invariants.keys()) == ["a"]
    assert list(kb._relations["2"]._invariants.keys()) == ["b"]
    assert list(kb._relations["3"]._invariants.keys()) == ["c"]
