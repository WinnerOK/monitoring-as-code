from pathlib import Path

from controller.state import State, StateData
from loguru import logger


class FileState(State):
    def __init__(
        self,
        file: Path,
        *,
        save_state: bool,
        persist_untracked: bool,
    ):
        super(FileState, self).__init__(
            save_state=save_state,
            persist_untracked=persist_untracked,
        )
        self.file = file

    def _load(self) -> None:
        if self.file.exists():
            self._data = StateData.parse_file(self.file)
        else:
            logger.info(
                f"State file {self.file.name} does not exists. "
                f"Initializing with empty storage"
            )

    def _save(self) -> None:
        with self.file.open("w") as f:
            logger.debug(f"Writing state to {self.file.name}")
            f.write(
                self._data.json(indent=2, sort_keys=True),
            )
