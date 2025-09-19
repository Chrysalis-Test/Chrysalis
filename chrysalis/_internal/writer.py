from typing import Self
from types import TracebackType

from tqdm import tqdm

# ASCII ART Credit: https://patorjk.com/software/taag.
_ASCII_ART_CHRYSALIS = """
   _____ _                          _ _
  / ____| |                        | (_)
 | |    | |__  _ __ _   _  __ _ ___| |_ ___
 | |    | '_ \\| '__| | | |/ _` / __| | / __|
 | |____| | | | |  | |_| | (_| \\__ | | \\__ \\
  \\_____|_| |_|_|   \\__, |\\__,_|___|_|_|___/
                     __/ |
                    |___/
"""


class Writer:
    """Display the metamorphic engine progess to the user."""

    def __init__(
        self,
        chain_length: int,
        num_chains: int,
    ) -> None:
        # ASCII escape code cause printed ASCII art to be purple.
        print("\033[35m" + _ASCII_ART_CHRYSALIS + "\033[0m")

        self._chain_length = chain_length
        self._num_chains = num_chains
        self._pbar: tqdm | None = None

    def __enter__(self) -> Self:
        self._pbar = tqdm(total=self._chain_length * self._num_chains)
        return self

    def report_finished_test_case(self) -> None:
        """A handle for an engine process to call when a test case completes."""
        if self._pbar is None:
            return None

        self._pbar.update()

    def __exit__(
        self,
        exc: type[BaseException] | None,
        value: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        if self._pbar is None:
            raise RuntimeError(
                "Attempted to close a writer context when no context exists."
            )
        self._pbar.close()
        self._pbar = None
