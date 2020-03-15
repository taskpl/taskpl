import uvicorn
import os
from fastapi import FastAPI
from loguru import logger
import sys
import functools

from taskpl.manager import JobManager, Job
from taskpl.task import Task
from taskpl.config import global_config

app = FastAPI()


def error_wrap(func):
    @functools.wraps(func)
    def _wrap(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(e)
            logger.error(sys.exc_info())
            return {"error": str(e)}

    return _wrap


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/api/v1/job/single")
@error_wrap
def job_create(*, task_name: str, job_name: str):
    try:
        # find
        task = Task.get_task_by_name(task_name)
        # new
        manager = JobManager()
        assert not manager.is_job_existed(
            task, job_name
        ), f"job {job_name} already existed"
        job = Job(task, job_name)
        job.init()
        return job
    except Exception as e:
        logger.error(sys.exc_info()[0])
        return {"error": str(e)}


@app.get("/api/v1/job/single")
@error_wrap
def job_retrieve(*, task_name: str, job_name: str):
    # find
    task = Task.get_task_by_name(task_name)
    # new
    manager = JobManager()
    job = manager.query_single_job(task, job_name)
    job.update_status()
    return job


@app.get("/api/v1/job/single/list")
@error_wrap
def job_retrieve_list(*, task_name: str, job_name: str):
    job = job_retrieve(task_name=task_name, job_name=job_name)
    if isinstance(job, Exception):
        return job
    return job.to_list()


@app.get("/api/v1/job/single/tree")
@error_wrap
def job_retrieve_tree(*, task_name: str, job_name: str):
    job = job_retrieve(task_name=task_name, job_name=job_name)
    if isinstance(job, Exception):
        return job
    return [job.pipeline.root]


@app.get("/api/v1/job/all")
@error_wrap
def job_all_retrieve(*, task_name: str):
    # find
    task = Task.get_task_by_name(task_name)
    # new
    manager = JobManager()
    # todo job object contains too much contents
    return manager.query_all_job(task)


@app.get("/api/v1/task/single")
@error_wrap
def task_retrieve(*, task_name: str):
    return Task.get_task_by_name(task_name)


@app.get("/api/v1/task/all")
@error_wrap
def task_all_retrieve():
    # todo this design looks a little weird
    return [
        os.path.splitext(each)[0]
        for each in os.listdir(global_config.SERVER_TASK_HOME)
        if each.endswith(global_config.TASK_CONFIG_FILE_TYPE)
    ]


class Server(object):
    def __init__(self):
        self.app = app

    def start(self):
        uvicorn.run(self.app, host="0.0.0.0", port=global_config.SERVER_PORT)
