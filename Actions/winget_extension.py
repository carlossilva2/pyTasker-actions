from logging import Logger

from Tasker.common import alias, ref
from Tasker.inspector import implements
from Tasker.types import OperationType as Operation
from Tasker.types import ParserType as Parser
from Tasker.types import Task
from yaspin import yaspin
from subprocess import call as shell


@implements(Operation)
class Extension(Operation):
    "Winget Action"

    __annotations__ = {
        "name": "Winget Install Action",
        "intent": "Install Applications via Winget",
    }

    def __init__(self, ctx: Parser, task: Task, logger: Logger) -> None:
        self.context = ctx  # Parser Context
        self.task = task  # Current assigned Task
        self.logger = logger
        self.affected_files: list[str] = []
        self.__internal_state = True  # Faulty execution flag
        self._type = "winget"
        ref(self)
        alias(self)

    def execute(self) -> None:
        with yaspin(text=f"Installing {self.task['package-name']}", color="yellow", timer=True) as spin:
            try:
                shell(f"winget install --id={self.task['package-id']} -e", shell=True)
                spin.text = "Install Completed"
                spin.ok("[DONE]")
            except Exception:
                spin.text = "Install Failed"
                spin.fail("[FAIL]")

    def rollback(self) -> None:
        pass

    def set_state(self, state: bool) -> None:
        "Sets the state for the Internal Fault flag"
        self.__internal_state = state

    def get_state(self) -> bool:
        "Returns the of the Internal Fault flag"
        return self.__internal_state
