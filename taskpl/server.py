import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
import os

from taskpl.manager import JobManager
from taskpl.task import Task
from taskpl.config import global_config


class JsonRequestModel(BaseModel):
    """ for parsing args of request only """

    # for matching models
    task_name: str = ""
    job_name: str = ""


app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/api/v1/task/new")
def task_new(*, request: JsonRequestModel):
    try:
        task_name = request.task_name
        job_name = request.job_name

        # find
        task = Task()
        task_config_path = os.path.join(global_config.SERVER_TASK_HOME, task_name) + ".toml"
        task.load(task_config_path)
        # new
        manager = JobManager()
        job = manager.new_job(task, job_name)
        job.init()
        return job
    except Exception as e:
        return {"error": str(e)}


class Server(object):
    def start(self):
        uvicorn.run(
            app, host="0.0.0.0", port=global_config.SERVER_PORT
        )
