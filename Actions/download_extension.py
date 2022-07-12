from logging import WARNING, Logger, getLogger

import requests
from Tasker.common import alias, ref
from Tasker.inspector import implements
from Tasker.types import OperationType as Operation
from Tasker.types import ParserType as Parser
from Tasker.types import Task
from validators import ValidationFailure, url
from yaspin import yaspin


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
        with yaspin(text="Downloading", color="yellow", timer=True) as spin:
            try:
                if isinstance(url(self.task["url"]), ValidationFailure):
                    spin.write("Invalid URL")
                    raise ValidationFailure(
                        url, {"value": self.task["url"], "public": False}
                    )
                file = requests.get(
                    self.task["url"],
                    allow_redirects=True,
                )
                spot = "." if self.task["file-type"] != "" else ""
                open(
                    f"{self.task['download-path']}/{self.task['file-name']}{spot}{self.task['file-type']}",
                    "wb",
                ).write(file.content)
                spin.text = "Download Complete"
                spin.ok("✅")
            except Exception:
                spin.text = "Download Failed"
                spin.fail("❌")

    def rollback(self) -> None:
        pass

    def set_state(self, state: bool) -> None:
        "Sets the state for the Internal Fault flag"
        self.__internal_state = state

    def get_state(self) -> bool:
        "Returns the of the Internal Fault flag"
        return self.__internal_state
