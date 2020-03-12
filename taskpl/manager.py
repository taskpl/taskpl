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
        space = os.path.join(
            global_config.WORKSPACE, self.task_type.name, self.job_name
        )
        self.workspace: str = space

    def is_inited(self) -> bool:
        return os.path.isdir(self.workspace)

    def init(self):
        # workspace
        os.makedirs(os.path.dirname(self.workspace), exist_ok=True)
        os.makedirs(self.workspace)

        # sub dirs
        def _create_dirs(stage_dict: dict, cur_path: str):
            for k, v in stage_dict.items():
                # not the end?
                if isinstance(v, dict):
                    # cur layer
                    sub_path = os.path.join(cur_path, k)
                    os.makedirs(sub_path, exist_ok=True)
                    _create_dirs(v, sub_path)
                # do nothing if end

        _create_dirs(self.task_type.pipeline.data, self.workspace)

    def status(self) -> dict:
        stage_dict = copy.deepcopy(self.task_type.pipeline.data)

        for cur_dir, cur_sub_dirs, cur_files in os.walk(self.workspace):
            cur_dir = cur_dir.replace(self.workspace, "")
            cur_dict = stage_dict
            for each in cur_dir.split(os.sep):
                # the first is always empty
                if not each:
                    continue
                # ignore error
                if each in cur_dict:
                    tmp = cur_dict[each]
                    if not isinstance(tmp, dict):
                        break
                    cur_dict = tmp
            else:
                # todo: filter?
                cur_dict["result"] = bool(cur_files) or bool(cur_sub_dirs)

        return stage_dict


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
        return [Job(task_type, each) for each in os.listdir(task_type.workspace)]
