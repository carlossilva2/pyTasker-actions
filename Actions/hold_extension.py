from logging import Logger

from Tasker.common import alias, ref
from Tasker.inspector import implements
from Tasker.types import OperationType as Operation
from Tasker.types import ParserType as Parser
from Tasker.types import Task

import time

@implements(Operation)
class Extension(Operation):
    "Hold Action"

    __annotations__ = {
        "name": "Hold Action",
        "intent": "Prevents InstructionSet from advancing until condition is met",
    }

    def __init__(self, ctx: Parser, task: Task, logger: Logger) -> None:
        self.context = ctx  # Parser Context
        self.task = task  # Current assigned Task
        self.logger = logger
        self.affected_files: list[str] = []
        self.__internal_state = True  # Faulty execution flag
        self._type = "hold"
        ref(self)
        alias(self)

    def execute(self) -> None:
        if self.task["type"] == "time":
            time_array = self.task["condition"].split(":")[0]
            while time.strftime("%H") != time_array[0] and time.strftime("%M") != time_array[1] and time.strftime("%S") != time_array[2]:
                pass
            print(time.strftime("%H:%M:%S"))

    def rollback(self) -> None:
        pass

    def set_state(self, state: bool) -> None:
        "Sets the state for the Internal Fault flag"
        self.__internal_state = state

    def get_state(self) -> bool:
        "Returns the of the Internal Fault flag"
        return self.__internal_state