from logmachine import ContribLog
import os, sys, logging

logger = ContribLog(
    "",
    debug_level=os.getenv('DEBUG_LEVEL', 0),
    verbose="--verbose" in sys.argv,
#    central={
#        "url": "https://logmachine.bufferpunk.com",
#        "room": "bio-zk-monitoring",
#        "headers": {}
#    },
#   socketio=True
)

logging.getLogger("pymongo.client").setLevel(0)
logging.getLogger("pymongo.command").setLevel(0)
logging.getLogger("pymongo.serverSelection").setLevel(0)
logging.getLogger("pymongo.connection").setLevel(0)
logging.getLogger("pymongo.topology").setLevel(0)
