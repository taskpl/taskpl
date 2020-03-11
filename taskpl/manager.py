from taskpl.task import Task
from taskpl.config import global_config

import os
import typing


class Job(object):
    def __init__(self, task_type: Task, job_name: str):
        self.task_type: Task = task_type
        self.job_name: str = job_name
        self.workspace: str = ""

    def init(self):
        # workspace
        space = os.path.join(global_config.WORKSPACE, self.task_type.name, self.job_name)
        assert not os.path.isdir(space), f"path {space} has been used"
        os.makedirs(space, exist_ok=True)
        self.workspace = space

        # sub dirs
        # todo multiple layers?
        for each in self.task_type.pipeline.data.keys():
            sub_path = os.path.join(space, each)
            os.makedirs(sub_path, exist_ok=True)

    def status(self) -> typing.Iterator:
        return os.walk(self.workspace)


class JobManager(object):
    def new_job(self, task_type: Task, job_name: str) -> Job:
        return Job(task_type, job_name)
