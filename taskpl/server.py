import uvicorn
import os
from fastapi import FastAPI

from taskpl.manager import JobManager, Job
from taskpl.task import Task
from taskpl.config import global_config

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


# todo: use decorator for error handler
@app.post("/api/v1/job/single")
def job_create(*, task_name: str, job_name: str):
    try:
        # find
        task = Task.get_task_by_name(task_name)
        # new
        manager = JobManager()
        assert not manager.is_job_existed(task, job_name), f"job {job_name} already existed"
        job = Job(task, job_name)
        job.init()
        return job
    except Exception as e:
        return {"error": str(e)}


@app.get("/api/v1/job/single")
def job_retrieve(*, task_name: str, job_name: str):
    try:
        # find
        task = Task.get_task_by_name(task_name)
        # new
        manager = JobManager()
        job = manager.query_single_job(task, job_name)
        return job.status()
    except Exception as e:
        return {"error": str(e)}


@app.get("/api/v1/job/all")
def job_all_retrieve(*, task_name: str):
    try:
        # find
        task = Task.get_task_by_name(task_name)
        # new
        manager = JobManager()
        # todo job object contains too much contents
        return manager.query_all_job(task)
    except Exception as e:
        return {"error": str(e)}


@app.get("/api/v1/task/single")
def task_retrieve(*, task_name: str):
    try:
        return Task.get_task_by_name(task_name)
    except Exception as e:
        return {"error": str(e)}


@app.get("/api/v1/task/all")
def task_all_retrieve():
    try:
        # todo this design looks a little weird
        return [
            os.path.splitext(each)[0]
            for each in os.listdir(global_config.WORKSPACE)
            if each.endswith("toml")
        ]
    except Exception as e:
        return {"error": str(e)}


class Server(object):
    def __init__(self):
        self.app = app

    def start(self):
        uvicorn.run(
            self.app, host="0.0.0.0", port=global_config.SERVER_PORT
        )
