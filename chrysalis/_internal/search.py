import random
from abc import ABC, abstractmethod
from typing import assert_never
from enum import Enum

from chrysalis._internal.tables.relation import KnowledgeBase, Relation


class SearchGenerator(ABC):
    def __init__(self, knowledge_base: KnowledgeBase) -> None:
        self._knowledge_base = knowledge_base

    @abstractmethod
    def __next__(self) -> Relation:
        pass


class SearchStrategy(Enum):
    """Possible search strategies when creating metamorphic relation chains."""

    RANDOM = 1


class RandomGenerator(SearchGenerator):
    def __init__(self, knowledge_base: KnowledgeBase) -> None:
        super().__init__(knowledge_base=knowledge_base)

        self._relations = list(self._knowledge_base.relations.values())
        self._indicies = list(range(len(self._relations)))

    def __next__(self) -> Relation:
        choice = random.choices(self._indicies, k=1)[0]
        return self._relations[choice]


class SearchSpace:
    """A handle to interact with the search space for a knowledge base."""

    def __init__(
        self,
        knowledge_base: KnowledgeBase,
        strategy: SearchStrategy = SearchStrategy.RANDOM,
    ):
        self._knowledge_base = knowledge_base
        self._strategy = strategy

    def create_generator(self) -> SearchGenerator:
        """Used to generate metamorphic chains based on search strategy."""
        match self._strategy:
            case SearchStrategy.RANDOM:
                return RandomGenerator(knowledge_base=self._knowledge_base)
            case _:
                assert_never(self.value)
