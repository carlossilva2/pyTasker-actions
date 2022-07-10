from logging import Logger
from time import time

from Tasker.common import alias, ref
from Tasker.inspector import implements
from Tasker.types import OperationType as Operation
from Tasker.types import ParserType as Parser
from Tasker.types import Task


@implements(Operation)
class Extension(Operation):
    "sleep Action"

    __annotations__ = {
        "name": "sleep Action",
        "intent": "Simple Sleep Action",
    }

    def __init__(self, ctx: Parser, task: Task, logger: Logger) -> None:
        self.context = ctx  # Parser Context
        self.task = task  # Current assigned Task
        self.logger = logger
        self.affected_files: list[str] = []
        self.__internal_state = True  # Faulty execution flag
        self._type = "Custom"
        ref(self)
        alias(self)

    def execute(self) -> None:
        supposed = time() + int(self.task["amount"])
        while supposed >= time():
            pass

    def rollback(self) -> None:
        # Rollback Block
        pass

    def set_state(self, state: bool) -> None:
        "Sets the state for the Internal Fault flag"
        self.__internal_state = state

    def get_state(self) -> bool:
        "Returns the of the Internal Fault flag"
        return self.__internal_state