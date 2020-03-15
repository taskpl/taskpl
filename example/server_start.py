from taskpl.server import Server
from starlette.middleware.cors import CORSMiddleware

s = Server()
s.app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
s.start()
