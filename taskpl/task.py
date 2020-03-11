import os
import toml
import typing
from collections import OrderedDict

from taskpl.config import global_config


class TaskConfig(object):
    LABEL = "config"

    def __init__(self, data: OrderedDict):
        self.data: OrderedDict = data
        self.name = self.data["name"]


class TaskPipeline(object):
    LABEL = "pipeline"

    def __init__(self, data: OrderedDict):
        self.data: OrderedDict = data


class Task(object):
    def __init__(self):
        # user config file
        self.name: str = ""
        self.path: str = ""

        # field in config file
        self.raw_dict: dict = dict()
        self.config: typing.Optional[TaskConfig] = None
        self.pipeline: typing.Optional[TaskPipeline] = None

    def load(self, path: str):
        # file -> object
        assert os.path.isfile(path), f"no file found in {path}"
        self.path = path
        with open(self.path) as f:
            self.raw_dict = toml.load(f)
        # parse
        self.config = TaskConfig(self.raw_dict[TaskConfig.LABEL])
        self.pipeline = TaskPipeline(self.raw_dict[TaskPipeline.LABEL])
        self.name = self.config.name

    @classmethod
    def get_task_by_name(cls, task_name: str) -> "Task":
        task = Task()
        task_config_path = os.path.join(global_config.SERVER_TASK_HOME, task_name) + ".toml"
        task.load(task_config_path)
        return task
