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


class TaskPipelineStage(object):
    def __init__(self, name: str, sub_stage: typing.List["TaskPipelineStage"], parent_stage_name: str = None):
        self.name = name
        self.sub_stages = sub_stage
        # avoid recursive function calling
        # so use string, not an object
        self.parent_stage_name = parent_stage_name

        # optional
        self.desc: str = ""
        self.strict: bool = True

    def inject_kwargs(self, **kwargs):
        # optional fields
        self.__dict__.update(kwargs)

    @classmethod
    def create_stage_tree(cls, data: dict) -> "TaskPipelineStage":
        def _parse_data(name: str, cur_node: dict, parent_node: TaskPipelineStage = None) -> "TaskPipelineStage":
            result = TaskPipelineStage(name, [], parent_node.name if parent_node else None)
            for each_stage_name, content in cur_node.items():
                if isinstance(content, dict):
                    sub_stage = _parse_data(each_stage_name, content, result)
                    result.sub_stages.append(sub_stage)
                else:
                    # end node
                    result.inject_kwargs(**cur_node)
            return result

        return _parse_data(global_config.TASK_ROOT_NAME, data)


class TaskPipeline(object):
    LABEL = "pipeline"
    ROOT_NAME = "root"

    def __init__(self, data: OrderedDict):
        self.data: OrderedDict = data
        self.root_node = TaskPipelineStage.create_stage_tree(data)

    def get_stage_by_name(self, name: str) -> TaskPipelineStage:
        def _inner(cur_node: TaskPipelineStage):
            if name == cur_node.name:
                return cur_node
            for each in cur_node.sub_stages:
                res = _inner(each)
                # found?
                if res:
                    return res
        return _inner(self.root_node)


class Task(object):
    def __init__(self):
        # user config file
        self.name: str = ""
        self.path: str = ""

        # field in config file
        self.raw: dict = dict()
        self.config: typing.Optional[TaskConfig] = None
        self.pipeline: typing.Optional[TaskPipeline] = None
        self.workspace: typing.Optional[str] = None

    def load(self, path: str):
        # file -> object
        assert os.path.isfile(path), f"no file found in {path}"
        self.path = path
        with open(self.path, encoding=global_config.CHARSET) as f:
            self.raw = toml.load(f)
        # parse
        self.config = TaskConfig(self.raw[TaskConfig.LABEL])
        self.pipeline = TaskPipeline(self.raw[TaskPipeline.LABEL])
        # extras
        self.name = self.config.name
        self.workspace = os.path.join(global_config.WORKSPACE, self.name)

    @classmethod
    def get_task_by_name(cls, task_name: str) -> "Task":
        task = Task()
        task_config_path = (
            os.path.join(global_config.SERVER_TASK_HOME, task_name)
            + "."
            + global_config.TASK_CONFIG_FILE_TYPE
        )
        task.load(task_config_path)
        return task
