from collections.abc import Callable
from pathlib import Path

import duckdb

from chrysalis._internal.tables.defs import TemporarySqlite3RelationConnection
from chrysalis._internal.engine import Engine
from chrysalis._internal.tables.relation import KnowledgeBase
from chrysalis._internal.search import SearchSpace, SearchStrategy
from chrysalis._internal.writer import Writer

_CURRENT_KNOWLEDGE_BASE: KnowledgeBase | None = None
"""
The current knowledge space for the module.

It is possible to "hack" the module to create a single source of truth knowledge base.
This allows repeated calls to `register` to add relations the same knowledge base
and for the knowledge base to be reset. It is important that this global variable start
uninitialized so that its generic can be specified at run time.
"""


def reset_knowledge_base() -> None:
    """Initialize a new knowledge base for the module."""
    global _CURRENT_KNOWLEDGE_BASE  # NOQA: PLW0603
    _CURRENT_KNOWLEDGE_BASE = KnowledgeBase()


def get_knowledge_base() -> KnowledgeBase | None:
    """Fetch the knowledge base of the current session."""
    global _CURRENT_KNOWLEDGE_BASE  # NOQA: PLW0603
    return _CURRENT_KNOWLEDGE_BASE


def register[T, R](
    transformation: Callable[[T], T],
    invariant: Callable[[R, R], bool],
) -> None:
    """Register a metamorphic relation into the current knowledge base."""
    global _CURRENT_KNOWLEDGE_BASE  # NOQA: PLW0603
    if _CURRENT_KNOWLEDGE_BASE is None:
        _CURRENT_KNOWLEDGE_BASE = KnowledgeBase()

    _CURRENT_KNOWLEDGE_BASE.register(
        transformation=transformation,
        invariant=invariant,
    )


def run[T, R](
    sut: Callable[[T], R],
    input_data: list[T],
    search_strategy: SearchStrategy = SearchStrategy.RANDOM,
    chain_length: int = 10,
    num_chains: int = 10,
    persistent_db_path: Path | None = None,
) -> duckdb.DuckDBPyConnection:
    """
    Run metamorphic testing on the SUT using previously registered relations.

    Parameters
    ----------
    sut : Callable[[T], R]
        The 'system under test' that is currenting being tested.
    input_data : list[T]
        The input data to be transformed and used as input into the SUT. Each input
        object in the input data should be serializable by pickling.
    search_strategy : SearchStrategy, optional
        The search strategy to use when generating metamorphic relation chains. The
        serach strategy defaults to `SearchStrategy.RANDOM`.
    chain_length : int, optional
        The number of relations in each generated metamorphic relation chain. The chain
        length defaults to 10.
    num_chains : int, optional
        The number of metamorphic chains to generate. The number of chains defaults to
        10.
    persistent_db_path : Path, optional
        The location to save the database file for the resultant duckdb connection. If
        no value is specified, the duckdb connection is made in-memory and thus the
        data in the connection is lost when the processes exits.
    """
    if _CURRENT_KNOWLEDGE_BASE is None:
        raise RuntimeError(
            "No metamorphic relations have been registered in the current session, exiting."
        )

    with TemporarySqlite3RelationConnection(_CURRENT_KNOWLEDGE_BASE) as (
        conn,
        db_path,
    ):
        search_space = SearchSpace(
            knowledge_base=_CURRENT_KNOWLEDGE_BASE,
            strategy=search_strategy,
        )

        with Writer(chain_length=chain_length, num_chains=num_chains) as writer:
            engine = Engine(
                sut=sut,
                input_data=input_data,
                search_space=search_space,
                sqlite_conn=conn,
                sqlite_db=db_path,
                writer=writer,
            )
            engine.execute(
                chain_length=chain_length,
                num_chains=num_chains,
            )

        duckdb_conn = engine.results_to_duckdb(db_path=persistent_db_path)
        conn.close()

    return duckdb_conn
