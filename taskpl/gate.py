"""
Gate is designed for checking job stages' status

"""
import os
import typing
from loguru import logger


class BaseGate(object):
    def __init__(self):
        self.name = self.__class__.__name__

    def check(self, stage: "JobPipelineStage") -> bool:
        raise NotImplementedError("you are calling an abstract class")


class EmptyOrNotGate(BaseGate):
    def check(self, stage: "JobPipelineStage") -> bool:
        return bool(os.listdir(stage.workspace))


class SubAllGate(BaseGate):
    def check(self, stage: "JobPipelineStage") -> bool:
        return all([
            each.result for each in stage.sub_nodes
        ])


class SubAnyGate(BaseGate):
    def check(self, stage: "JobPipelineStage") -> bool:
        return any([
            each.result for each in stage.sub_nodes
        ])


def import_gate(name: str) -> typing.Optional[BaseGate]:
    if name not in __all__:
        logger.warning(f"gate {name} not existed")
        return None
    try:
        return globals()[name]()
    except ImportError as e:
        logger.warning(e)
        return None


# default
DefaultGate = EmptyOrNotGate


__all__ = ["BaseGate", "EmptyOrNotGate", "DefaultGate", "SubAllGate", "SubAnyGate", "import_gate"]
