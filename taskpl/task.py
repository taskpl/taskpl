import os
import toml
import typing
from collections import OrderedDict
from planter import Tree, Node, Compiler

from taskpl.config import global_config
from taskpl.gate import import_gate


class TaskConfig(object):
    LABEL = "config"

    def __init__(self, data: OrderedDict):
        self.data: OrderedDict = data
        self.name = self.data["name"]


class TaskPipelineStage(Node):
    def __init__(self, *args, **kwargs):
        # optional
        self.desc: str = ""
        self.strict: bool = True
        # todo how to send args to gate object?
        self.gate: typing.List = ["DefaultGate"]
        super(TaskPipelineStage, self).__init__(*args, **kwargs)

    def convert_special_attrs(self):
        # special operations
        # gate
        assert isinstance(self.gate, list), "gates must be a list"
        self.gate = [import_gate(each) for each in self.gate]

    def __str__(self):
        return f"<PipelineStage name={self.name} id={id(self)}>"

    __repr__ = __str__


class TaskCompiler(Compiler):
    NODE_KLS = TaskPipelineStage
    ROOT_NODE_NAME = "root"


class TaskPipeline(Tree):
    LABEL = "pipeline"
    COMPILER = TaskCompiler

    def __init__(self, data: OrderedDict):
        self.data = data
        tc = self.COMPILER()
        root = tc.compile(data)

        super(TaskPipeline, self).__init__(root)

        # handle special attrs
        for each in self.loop_stages():
            each.convert_special_attrs()

    def loop_stages(self, without_root: bool = None):
        if without_root:
            it = self.dfs(self.root)
            next(it)
            return it
        return self.dfs(self.root)

    get_stage_by_name = Tree.get_node


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
