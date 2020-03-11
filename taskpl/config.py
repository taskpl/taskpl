import os


class _Config(object):
    PROJECT_ROOT_PATH = os.path.dirname(os.path.dirname(__file__))
    # default
    WORKSPACE = "."


global_config = _Config()
