import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel

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


@app.post("/api/v1/job/new")
def job_new(*, request: JsonRequestModel):
    try:
        task_name = request.task_name
        job_name = request.job_name

        # find
        task = Task.get_task_by_name(task_name)
        # new
        manager = JobManager()
        job = manager.query_job(task, job_name)
        job.init()
        return job
    except Exception as e:
        return {"error": str(e)}


@app.get("/api/v1/job/query")
def job_query(*, request: JsonRequestModel):
    try:
        task_name = request.task_name
        job_name = request.job_name

        # find
        task = Task.get_task_by_name(task_name)
        # new
        manager = JobManager()
        job = manager.query_job(task, job_name)
        assert job.is_inited(), f"job {job_name} is not existed"
        return job.status()
    except Exception as e:
        return {"error": str(e)}


class Server(object):
    def start(self):
        uvicorn.run(
            app, host="0.0.0.0", port=global_config.SERVER_PORT
        )
