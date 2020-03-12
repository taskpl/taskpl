from taskpl.task import Task
from taskpl.config import global_config

import os
import copy
import typing


class Job(object):
    def __init__(self, task_type: Task, job_name: str):
        self.task_type: Task = task_type
        self.job_name: str = job_name
        self.inited: bool = False
        # workspace
        # todo weird!!
        space = os.path.join(global_config.WORKSPACE, self.task_type.name, self.job_name)
        self.workspace: str = space

    def is_inited(self) -> bool:
        return os.path.isdir(self.workspace)

    def init(self):
        # workspace
        os.makedirs(self.workspace)

        # sub dirs
        # todo multiple layers?
        for each in self.task_type.pipeline.data.keys():
            sub_path = os.path.join(self.workspace, each)
            os.makedirs(sub_path, exist_ok=True)

    def status(self) -> dict:
        # todo multiple layers?
        # todo temp design
        result = copy.deepcopy(self.task_type.pipeline.data)
        for each_stage in os.listdir(self.workspace):
            sub_path = os.path.join(self.workspace, each_stage)
            result[each_stage]["result"] = bool(os.listdir(sub_path))
        return result


class JobManager(object):
    def is_job_existed(self, task_type: Task, job_name: str) -> bool:
        try:
            self.query_single_job(task_type, job_name)
            return True
        except FileNotFoundError:
            return False

    def query_single_job(self, task_type: Task, job_name: str) -> Job:
        if job_name in os.listdir(task_type.workspace):
            return Job(task_type, job_name)
        raise FileNotFoundError(f"job {job_name} is not existed")

    def query_all_job(self, task_type: Task) -> typing.List[Job]:
        return [
            Job(task_type, each)
            for each in os.listdir(task_type.workspace)
        ]
