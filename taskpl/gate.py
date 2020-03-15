"""
Gate is designed for checking job stages' status

"""
import os
import typing
from loguru import logger


class BaseGate(object):
    def __init__(self, *args):
        self.name = self.__class__.__name__
        self.args = args
        logger.debug(self.__dict__)

    def check(self, stage: "JobPipelineStage") -> bool:
        raise NotImplementedError("you are calling an abstract class")


class EmptyOrNotGate(BaseGate):
    def check(self, stage: "JobPipelineStage") -> bool:
        return bool(os.listdir(stage.workspace))


class SubAllGate(BaseGate):
    def check(self, stage: "JobPipelineStage") -> bool:
        return all([each.result for each in stage.sub_nodes])


class SubAnyGate(BaseGate):
    def check(self, stage: "JobPipelineStage") -> bool:
        return any([each.result for each in stage.sub_nodes])


class FileAllRequiredGate(BaseGate):
    def check(self, stage: "JobPipelineStage") -> bool:
        file_list = os.listdir(stage.workspace)
        for each in self.args:
            if each not in file_list:
                return False
        return True


class FileAnyRequiredGate(BaseGate):
    def check(self, stage: "JobPipelineStage") -> bool:
        file_list = os.listdir(stage.workspace)
        for each in self.args:
            if each in file_list:
                return True
        return False


def import_gate(name: str, stage: "JobPipelineStage") -> typing.Optional[BaseGate]:
    if name not in __all__:
        logger.warning(f"gate {name} not existed")
        return None
    # args
    if hasattr(stage, name):
        args = getattr(stage, name)
    else:
        args = []

    try:
        return globals()[name](*args)
    except ImportError as e:
        logger.warning(e)
        return None


# default
DefaultGate = EmptyOrNotGate


__all__ = [
    "BaseGate",
    "EmptyOrNotGate",
    "DefaultGate",
    "SubAllGate",
    "SubAnyGate",
    "FileAllRequiredGate",
    "FileAnyRequiredGate",
    "import_gate",
]
