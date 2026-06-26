import sqlite3
from langgraph.checkpoint.sqlite import SqliteSaver

# SQLite persists checkpoint state to disk.
# This means if a node crashes, we can resume from the last saved checkpoint.
# check_same_thread=False is needed because FastAPI uses multiple threads.

_conn = sqlite3.connect("checkpoints.db", check_same_thread=False)
checkpointer = SqliteSaver(_conn)
