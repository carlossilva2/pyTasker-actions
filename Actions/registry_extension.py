from logging import Logger

from Tasker.common import alias, ref
from Tasker.inspector import implements
from Tasker.types import OperationType as Operation
from Tasker.types import ParserType as Parser
from Tasker.types import Task

import winreg
# import os.path as Path
from os import listdir, remove
from typing import Dict, List, Literal, Tuple, Union

import win32api
import win32con
import win32security

ROOTS: Dict[str, int] = {
    "classes-root": winreg.HKEY_CLASSES_ROOT,
    "current-user": winreg.HKEY_CURRENT_USER,
    "current-config": winreg.HKEY_CURRENT_CONFIG,
    "local-machine": winreg.HKEY_LOCAL_MACHINE,
    "users": winreg.HKEY_USERS,
}

TYPES: Dict[str, int] = {
    "sz": winreg.REG_SZ,
    "multisz": winreg.REG_MULTI_SZ,
    "none": winreg.REG_NONE,
    "binary": winreg.REG_BINARY,
    "dword": winreg.REG_DWORD,
    "qword": winreg.REG_QWORD,
}

RootKeys = Literal[
    "classes-root", "current-user", "current-config", "local-machine", "users"
]
TypeList = Literal["sz", "multisz", "none", "binary", "dword", "qword"]


def parse_input(k: str) -> Tuple[int, List[str]]:
    if k == "":
        raise Exception("Cannot provide empty Registry Path")
    str_list = k.split(">")
    root: int = ROOTS[str_list[0]]
    str_list.pop(0)
    return (root, [_ for _ in str_list if _ != ""])


def get_type(key: TypeList) -> int:
    ans = TYPES.get(key)
    return ans if ans != None else TYPES["sz"]


def get_all_keys(root: RootKeys) -> List[str]:
    keys = []
    i = 0
    try:
        _ = ROOTS[root]
        while True:
            k = winreg.EnumKey(_, i)
            keys.append(k)
            i += 1
    except Exception:
        pass
    return keys


def create_key(path: str, key_name: str) -> None:
    k = parse_input(path)
    with winreg.OpenKey(
        k[0], r"\\".join(k[1]), reserved=0, access=winreg.KEY_CREATE_SUB_KEY
    ) as key:
        winreg.CreateKeyEx(key, key_name)


def set_key_value(path: str, name: str, _type: int, value: Union[str, int]) -> None:
    k = parse_input(path)
    with winreg.OpenKey(
        k[0], r"\\".join(k[1]), reserved=0, access=winreg.KEY_SET_VALUE
    ) as key:
        winreg.SetValueEx(key, name, 0, _type, value)


def get_key_value(path: str, logger: Logger) -> Union[str, None]:
    k = parse_input(path)
    v = k[1][-1]
    k[1].pop(-1)
    with winreg.OpenKey(k[0], r"\\".join(k[1]), access=winreg.KEY_READ) as key:
        try:
            return winreg.QueryValueEx(key, rf"{v}")[0]
        except Exception:
            logger.warning(f"No match for requested '{v}' Key Value")
            return ""


def backup(root: RootKeys, path: str, fname: str) -> None:
    files = listdir(path)
    if f"{fname}.reg" in files:
        remove(f"{path}/{fname}.reg")
    # r = winreg.ConnectRegistry(None, ROOTS[root])
    # with winreg.OpenKey(r, "", reserved=0, access=winreg.KEY_ALL_ACCESS) as key:
    with winreg.OpenKey(ROOTS[root], "") as key:
        pid = win32api.GetCurrentProcessId()
        ph = win32api.OpenProcess(win32con.PROCESS_ALL_ACCESS, 0, pid)
        th = win32security.OpenProcessToken(
            ph, win32security.TOKEN_ALL_ACCESS | win32con.TOKEN_ADJUST_PRIVILEGES
        )
        win32security.AdjustTokenPrivileges(
            th,
            0,
            (
                (
                    win32security.LookupPrivilegeValue("", win32security.SE_BACKUP_NAME),
                    win32con.SE_PRIVILEGE_ENABLED,
                ),
                (
                    win32security.LookupPrivilegeValue(
                        "", win32security.SE_SECURITY_NAME
                    ),
                    win32con.SE_PRIVILEGE_ENABLED,
                ),
            ),
        )
        winreg.SaveKey(key, f"{path}/{fname}.reg")

@implements(Operation)
class Extension(Operation):
    "Registry Action"

    __annotations__ = {
        "name": "Registry Action",
        "intent": "Change Windows Registry values/keys",
    }

    def __init__(self, ctx: Parser, task: Task, logger: Logger) -> None:
        if ctx.system != "Windows":
            ctx.abort(f"Operation not available on {ctx.system} Systems!")
        self.regex = r"\w>"
        self.context = ctx  # Parser Context
        self.task = task  # Current assigned Task
        self.logger = logger
        self.affected_files: list[str] = []
        self.__internal_state = True  # Faulty execution flag
        self._type = "registry"
        ref(self)
        alias(self)

    def execute(self) -> None:
        self.path = ">".join([self.task["start_key"], self.task["key"]])
        if self.task["function"] == "get":
            self.value = get_key_value(self.path, self.logger)
        elif self.task["function"] == "set":
            if self.task["value"] == "" or self.task["value"] == None:
                self.context.abort("No value was provided")
            self.safeguard = get_key_value(self.path, self.logger)
            parsed = parse_input(self.path)
            values = parsed[1]
            self.v = values[-1]
            values.pop()
            self.correct_path = ">".join([self.task["start_key"], *values])
            set_key_value(
                self.correct_path, self.v, get_type(self.task["type"]), self.task["value"]
            )
            self.value = get_key_value(self.path, self.logger)
        elif self.task["function"] == "create":
            create_key(self.path, self.task["value"])
        elif self.task["function"] == "backup":
            raise NotImplementedError(
                "Feature under development. Refer to future versions"
            )
            backup(self.task["start_key"], self.task["key"], self.task["rename"])

    def rollback(self) -> None:
        if self.task["function"] == "set":
            set_key_value(
                self.correct_path, self.v, get_type(self.task["type"]), self.safeguard
            )
            self.logger.warn(f"Rolled back \"{self.task['name']}\" task")

    def set_state(self, state: bool) -> None:
        "Sets the state for the Internal Fault flag"
        self.__internal_state = state

    def get_state(self) -> bool:
        "Returns the of the Internal Fault flag"
        return self.__internal_state