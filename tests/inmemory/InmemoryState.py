from monitor.controller.state import RESOURCE_ID_MAPPING, State, StateData


class InmemoryState(State):
    def __init__(
        self,
        saved_data: RESOURCE_ID_MAPPING,
        *,
        save_state: bool,
        persist_untracked: bool,
    ):
        super().__init__(save_state=save_state, persist_untracked=persist_untracked)
        self._data.resources = saved_data

    @property
    def internal_state(self) -> StateData:
        return self._data

    def _load(self) -> None:
        pass

    def _save(self) -> None:
        pass
