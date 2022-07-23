from logging import WARNING, Logger, getLogger

from Tasker.common import alias, ref
from Tasker.inspector import implements
from Tasker.types import OperationType as Operation
from Tasker.types import ParserType as Parser
from Tasker.types import Task

import sqlite3


@implements(Operation)
class Extension(Operation):
    "Download Action"

    __annotations__ = {
        "name": "Download Action",
        "intent": "Retrieves a file from a given URL",
    }

    def __init__(self, ctx: Parser, task: Task, logger: Logger) -> None:
        getLogger("requests").setLevel(WARNING)
        getLogger("urllib3").setLevel(WARNING)
        self.context = ctx  # Parser Context
        self.task = task  # Current assigned Task
        self.logger = logger
        self.affected_files: list[str] = []
        self.__internal_state = True  # Faulty execution flag
        self._type = "download"
        ref(self)
        alias(self)

    def execute(self) -> None:
        pass

    def rollback(self) -> None:
        pass

    def set_state(self, state: bool) -> None:
        "Sets the state for the Internal Fault flag"
        self.__internal_state = state

    def get_state(self) -> bool:
        "Returns the of the Internal Fault flag"
        return self.__internal_state
