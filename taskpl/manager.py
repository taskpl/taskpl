from taskpl.task import Task, TaskPipelineStage, TaskPipeline

import os
import typing
from loguru import logger


class JobPipelineStage(TaskPipelineStage):
    def __init__(self, *args, **kwargs):
        super(JobPipelineStage, self).__init__(*args, **kwargs)
        self.result = None


class JobPipeline(TaskPipeline):
    STAGE_KLS = JobPipelineStage


class Job(object):
    def __init__(self, task_type: Task, job_name: str):
        self.task_type: Task = task_type
        self.job_pipeline = JobPipeline(task_type.pipeline.data)
        # extend task
        self.job_name: str = job_name
        self.inited: bool = False
        # workspace
        self.workspace: str = os.path.join(self.task_type.workspace, job_name)
        logger.info(f"job {job_name}: {self.__dict__}")

    def is_inited(self) -> bool:
        return os.path.isdir(self.workspace)

    def init(self):
        """ create dirs """
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

        _create_dirs(self.job_pipeline.data, self.workspace)

    def status(self) -> dict:
        for cur_dir, cur_sub_dirs, cur_files in os.walk(self.workspace):
            cur_dir = cur_dir.replace(self.workspace, "")
            for each in cur_dir.split(os.sep):
                # the first is always empty
                if not each:
                    continue
                # get current stage
                cur_stage = self.job_pipeline.get_stage_by_name(each)
                if cur_stage:
                    # now we have stage and its workspace
                    logger.debug(f"current workspace: {cur_dir}")
                    logger.debug(f"current stage: {cur_stage}")
                    cur_stage.result = bool(cur_files) or bool(cur_sub_dirs)

        return self.job_pipeline.root_node


class JobManager(object):
    """ get status from disk """
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
