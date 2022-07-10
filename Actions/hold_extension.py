import datetime
import time
from logging import Logger

from Tasker.common import alias, ref
from Tasker.inspector import implements
from Tasker.types import OperationType as Operation
from Tasker.types import ParserType as Parser
from Tasker.types import Task


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
            time_array = [int(_) for _ in self.task["condition"].split(":")]
            t = datetime.datetime.today()
            future = datetime.datetime(
                t.year,
                t.month,
                t.day,
                time_array[0],
                time_array[1],
                time_array[2],
            )
            if (
                t.hour >= time_array[0]
                and t.minute > time_array[1]
                and t.second > time_array[2]
            ):
                future += datetime.timedelta(days=1)
            time.sleep((future - t).total_seconds())
        elif self.task["type"] == "date":
            date_array = [int(_) for _ in self.task["condition"].split("-")]
            t = datetime.datetime.today()
            future = datetime.datetime(date_array[0], date_array[1], date_array[2])
            if (
                t.year > date_array[0]
                and t.month > date_array[1]
                and t.day > date_array[2]
            ):
                future += datetime.timedelta(days=365)
            time.sleep((future - t).total_seconds())
        elif self.task["type"] == "datetime":
            date_array = [
                int(_) for _ in self.task["condition"].split(" ")[0].split("-")
            ]
            time_array = [
                int(_) for _ in self.task["condition"].split(" ")[1].split(":")
            ]
            all_array = [*date_array, *time_array]
            t = datetime.datetime.today()
            future = datetime.datetime(
                all_array[0],
                all_array[1],
                all_array[2],
                all_array[3],
                all_array[4],
                all_array[5],
            )
            if (
                t.year >= all_array[0]
                and t.month >= all_array[1]
                and t.day >= all_array[2]
                and t.hour >= all_array[3]
            ):
                future += datetime.timedelta(days=1)
            time.sleep((future - t).total_seconds())

    def rollback(self) -> None:
        pass

    def set_state(self, state: bool) -> None:
        "Sets the state for the Internal Fault flag"
        self.__internal_state = state

    def get_state(self) -> bool:
        "Returns the of the Internal Fault flag"
        return self.__internal_state
