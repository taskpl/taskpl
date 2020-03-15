from taskpl.task import Task, TaskPipelineStage, TaskPipeline, TaskCompiler

import os
import typing
from loguru import logger


class JobPipelineStage(TaskPipelineStage):
    def __init__(self, *args, **kwargs):
        super(JobPipelineStage, self).__init__(*args, **kwargs)
        self.result: typing.Any = None
        self.workspace: str = ""

    def init_workspace(self):
        logger.debug(f"init job workspace: {self.name}")
        os.makedirs(self.workspace, exist_ok=True)

    def check_gate(self):
        if not self.workspace:
            logger.warning(f"job {self.name} 's workspace is empty")
            return
        # check and update
        self.result = True
        for each in self.gate:
            self.result = self.result and bool(each.check(self))


class JobCompiler(TaskCompiler):
    NODE_KLS = JobPipelineStage
    ROOT_NODE_NAME = "root"


class JobPipeline(TaskPipeline):
    COMPILER = JobCompiler


class Job(object):
    def __init__(self, task_type: Task, job_name: str):
        # init from task
        self.task_type: Task = task_type
        self.pipeline = JobPipeline(task_type.pipeline.data)
        # extend task
        self.name: str = job_name
        # workspace
        self.workspace: str = os.path.join(self.task_type.workspace, job_name)
        self.bind_workspace()
        self.init()
        # update
        self.update_status()

        logger.info(f"job {job_name}: {self.__dict__}")

    def bind_workspace(self):
        # bind workspaces to stages
        for cur_dir, cur_sub_dirs, cur_files in os.walk(self.workspace):
            cur_dir = cur_dir.replace(self.workspace + os.sep, "")
            for each in cur_dir.split(os.sep):
                # get current stage
                cur_stage = self.pipeline.get_stage_by_name(each)
                if cur_stage:
                    # now we have stage and its workspace
                    full_path = os.path.join(self.workspace, cur_dir)
                    logger.debug(f"bind {full_path} to {cur_stage}")
                    cur_stage.workspace = full_path

    def is_inited(self) -> bool:
        return os.path.isdir(self.workspace) and bool(os.listdir(self.workspace))

    def init(self):
        """ create dirs """
        # workspace
        os.makedirs(os.path.dirname(self.workspace), exist_ok=True)
        os.makedirs(self.workspace, exist_ok=True)

        for each in self.pipeline.loop_stages(without_root=True):
            each.init_workspace()

    def update_status(self):
        for each in self.pipeline.loop_stages(without_root=True):
            each.check_gate()

    def to_list(self) -> typing.List[JobPipelineStage]:
        result = list()
        for each in self.pipeline.loop_stages(without_root=True):
            result.append(each)
        return result


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
