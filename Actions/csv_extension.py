from logging import Logger

from Tasker.common import alias, ref
from Tasker.inspector import implements
from Tasker.types import OperationType as Operation
from Tasker.types import ParserType as Parser
from Tasker.types import Task

import csv
import os

@implements(Operation)
class Extension(Operation):
    "CSV Action"

    __annotations__ = {
        "name": "CSV Action",
        "intent": "Reads, Write and stores CSV data",
    }

    def __init__(self, ctx: Parser, task: Task, logger: Logger) -> None:
        self.context = ctx  # Parser Context
        self.task = task  # Current assigned Task
        self.logger = logger
        self.affected_files: list[str] = []

        self.rows = []
        self.headers = []

        self.__internal_state = True  # Faulty execution flag
        self._type = "csv"
        ref(self)
        alias(self)

    def execute(self) -> None:
        instance = None
        if self.task['action'] == "read":
            if not self.check_if_file_exists(self.task['file']):
                self.context.abort("File does not exist")
            with open(self.task['file'], 'r') as file:
                instance = csv.DictReader(file)
                acted = False
                for row in instance:
                    if not acted:
                        self.headers = row.keys()
                        acted = True
                    self.rows.append(row)
                file.close()
            if len(self.rows) == 0:
                self.logger.warn("No data was retrieved")
        elif self.task['action'] == "write":
            rows: list[dict[str, 'str | int | float | bool']] = self.task['rows']
            location: str = self.task['path']
            name: str = self.task['file']
            with open(f"{location}/{name}.csv", 'w') as file:
                instance = csv.DictWriter(file, fieldnames=rows[0].keys(), lineterminator='\n')
                instance.writeheader()
                instance.writerows(rows)
                file.close()

    def rollback(self) -> None:
        if self.task['action'] == 'write':
            os.remove(f"{self.task['path']}/{self.task['file']}.csv")
            self.logger.info(f"Rolled back Write action on {self.task['file']}.csv file")
        else:
            self.logger.info("Nothing to Rollback")

    def set_state(self, state: bool) -> None:
        "Sets the state for the Internal Fault flag"
        self.__internal_state = state

    def get_state(self) -> bool:
        "Returns the of the Internal Fault flag"
        return self.__internal_state

    def check_if_file_exists(self, file: str) -> bool:
        k = "/"
        if "\\" in file:
            k = "\\"
        files = os.listdir("/".join(file.split(k)[:-1]))
        if file.split(k)[-1] not in files:
            return False
        return True
