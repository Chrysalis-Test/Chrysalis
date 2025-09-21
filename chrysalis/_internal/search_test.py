import ast
import random

from chrysalis._internal import invariants
from chrysalis._internal.tables.relation import KnowledgeBase
from chrysalis._internal.search import SearchSpace, SearchStrategy
from chrysalis._internal.conftest import (
    identity,
    inverse,
)


def test_metamorphic_search_random() -> None:
    knowledge_base = KnowledgeBase[ast.Expression, float]()

    knowledge_base.register(
        transformation=identity,
        invariant=invariants.equals,
    )
    knowledge_base.register(
        transformation=inverse,
        invariant=invariants.not_equals,
    )

    search_space = SearchSpace(
        knowledge_base=knowledge_base, strategy=SearchStrategy.RANDOM
    )

    random.seed(0)
    generator = search_space.create_generator()
    relation_chain = [next(generator) for _ in range(10)]

    assert len(relation_chain) == 10
    assert set([relation.transformation_name for relation in relation_chain]) == {
        "identity",
        "inverse",
    }
