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
    "Discord Notification Action"

    __annotations__ = {
        "name": "Discord Notification Action",
        "intent": "Sends a Discord notification using a Webhook",
    }

    def __init__(self, ctx: Parser, task: Task, logger: Logger) -> None:
        getLogger("requests").setLevel(WARNING)
        getLogger("urllib3").setLevel(WARNING)
        self.context = ctx  # Parser Context
        self.task = task  # Current assigned Task
        self.logger = logger
        self.affected_files: list[str] = []
        self.__internal_state = True  # Faulty execution flag
        self._type = "discord"
        ref(self)
        alias(self)

    def execute(self) -> None:
        with yaspin(text="Sending", color="yellow", timer=True) as spin:
            try:
                if isinstance(url(self.task["url"]), ValidationFailure):
                    spin.write("Invalid URL")
                    raise ValidationFailure(
                        url, {"value": self.task["url"], "public": False}
                    )

                if "discord.com/api/webhook" not in self.task["url"]:
                    raise Exception("Not a discord link")

                params = {
                    "username": "pyTaskerBot",
                    "avatar_url": "",
                    "content": self.task["content"]
                }
                if "embedded" in self.task.keys():
                    params["embeds"] = self.task["embedded"]

                requests.post(
                    self.task["url"],
                    headers={
                        "Content-Type": "application/json"
                    },
                    params=params
                )
                spin.text = "Notification sent"
                spin.ok("[DONE]")
            except Exception:
                spin.text = "Notification Failed"
                spin.fail("[FAIL]")

    def rollback(self) -> None:
        pass

    def set_state(self, state: bool) -> None:
        "Sets the state for the Internal Fault flag"
        self.__internal_state = state

    def get_state(self) -> bool:
        "Returns the of the Internal Fault flag"
        return self.__internal_state
