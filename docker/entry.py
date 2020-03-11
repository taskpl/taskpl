from taskpl.config import global_config
import os

WORKSPACE = "/taskpl_workspace"

global_config.SERVER_PORT = 9410
global_config.SERVER_TASK_HOME = os.path.join(WORKSPACE, "task_home")
global_config.WORKSPACE = WORKSPACE

from taskpl.server import Server

s = Server()
s.start()
