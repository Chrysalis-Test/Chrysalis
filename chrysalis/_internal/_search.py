import random
from abc import ABC, abstractmethod
from typing import assert_never
from enum import Enum

from chrysalis._internal._relation import KnowledgeBase, Relation


class SearchGenerator(ABC):
    def __init__(self, knowledge_base: KnowledgeBase) -> None:
        self._knowledge_base = knowledge_base

    @abstractmethod
    def __next__(self) -> Relation:
        pass


class SearchStrategy(Enum):
    """Possible search strategies when creating metamorphic relation chains."""

    RANDOM = 1

    def get_generator(self, knowledge_base: KnowledgeBase) -> SearchGenerator:
        match self.value:
            case SearchStrategy.RANDOM.value:
                return RandomGenerator(knowledge_base=knowledge_base)
            case _:
                assert_never(self.value)


class RandomGenerator(SearchGenerator):
    def __init__(self, knowledge_base: KnowledgeBase) -> None:
        super().__init__(knowledge_base=knowledge_base)

        self._relations = list(self._knowledge_base.relations.values())
        self._n = len(self._relations)
        self._indicies = list(range(self._n))
        self._weights = [1.0 for _ in range(self._n)]

    def __next__(self) -> Relation:
        choice = random.choices(self._indicies, self._weights, k=1)[0]
        reduction = self._weights[choice] / 2

        addition = reduction / (self._n - 1)
        for i in range(self._n):
            if i == choice:
                self._weights[choice] = reduction
            else:
                self._weights[i] += addition

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
        return self._strategy.get_generator(knowledge_base=self._knowledge_base)
