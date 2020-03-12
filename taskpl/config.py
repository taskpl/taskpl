import os


class _Config(object):
    PROJECT_ROOT_PATH = os.path.dirname(os.path.dirname(__file__))
    # default
    WORKSPACE = "."
    CHARSET = "utf-8"
    # server
    SERVER_PORT = 9410
    SERVER_TASK_HOME = "."
    # task
    TASK_ROOT_NAME = "root"
    TASK_CONFIG_FILE_TYPE = "toml"


global_config = _Config()
