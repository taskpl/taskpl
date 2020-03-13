import os
import toml
import typing
from collections import OrderedDict
from loguru import logger

from taskpl.config import global_config
from taskpl.gate import BaseGate, DefaultGate, import_gate


class TaskConfig(object):
    LABEL = "config"

    def __init__(self, data: OrderedDict):
        self.data: OrderedDict = data
        self.name = self.data["name"]


class TaskPipelineStage(object):
    def __init__(
        self,
        name: str,
        sub_stage: typing.List["TaskPipelineStage"],
        parent_stage_name: str = None,
    ):
        self.name = name
        self.sub_stages = sub_stage
        # avoid recursive function calling
        # so use string, not an object
        self.parent_stage_name = parent_stage_name

        # optional
        self.desc: str = ""
        self.strict: bool = True
        self.gate: typing.List[BaseGate] = [
            DefaultGate(),
        ]

    def inject_kwargs(self, **kwargs):
        # ignore sub dict
        for k, v in kwargs.items():
            # special options
            if k == "gate":
                assert isinstance(v, list), "gates must be a list"
                # clean the origin list
                self.gate = []
                # append gates
                for each_gate_name in v:
                    each_gate = import_gate(each_gate_name)
                    assert each_gate, f"gate {each_gate_name} not existed"
                    self.gate.append(each_gate)
                    logger.debug(f"injecting gate: ({k}: {v}) to {self.name}")
                continue

            # only allow these types
            if isinstance(v, (str, int, list)):
                logger.debug(f"injecting: ({k}: {v}) to {self.name}")
                self.__dict__[k] = v

    @classmethod
    def create_stage_tree(
        cls, data: dict, stage_kls: typing.Type["TaskPipelineStage"]
    ) -> "TaskPipelineStage":
        def _parse_data(
            name: str, cur_node: dict, parent_node: TaskPipelineStage = None
        ) -> "TaskPipelineStage":
            result = stage_kls(name, [], parent_node.name if parent_node else None)
            for each_stage_name, content in cur_node.items():
                if isinstance(content, dict):
                    sub_stage = _parse_data(each_stage_name, content, result)
                    result.sub_stages.append(sub_stage)
                else:
                    # end node
                    result.inject_kwargs(**cur_node)
            return result

        return _parse_data(global_config.TASK_ROOT_NAME, data)

    def __str__(self):
        return f"<PipelineStage name={self.name} id={id(self)}>"

    __repr__ = __str__


class TaskPipeline(object):
    LABEL = "pipeline"
    ROOT_NAME = "root"
    STAGE_KLS = TaskPipelineStage

    def __init__(self, data: OrderedDict):
        self.data: OrderedDict = data
        self.root_node = TaskPipelineStage.create_stage_tree(data, self.STAGE_KLS)

    def loop_stages(self):
        def _loop_node(node: TaskPipelineStage):
            yield node
            for each in node.sub_stages:
                yield from _loop_node(each)

        return _loop_node(self.root_node)

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
        os.makedirs(self.workspace, exist_ok=True)

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

    def __str__(self):
        return f"<Task name={self.name} id={id(self)}>"

    __repr__ = __str__
