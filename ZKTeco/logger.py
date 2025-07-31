from logmachine import ContribLog
import os, sys

logger = ContribLog("", debug_level=os.getenv('DEBUG_LEVEL', 0), verbose="--verbose" in sys.argv)
