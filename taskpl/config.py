import os


class _Config(object):
    PROJECT_ROOT_PATH = os.path.dirname(os.path.dirname(__file__))
    # default
    WORKSPACE = "."
    # server
    SERVER_PORT = 9410
    SERVER_TASK_HOME = "."


global_config = _Config()
