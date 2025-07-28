from datetime import datetime
import os, sys

class Logger:
    def __init__(self, verbose=False, debug_level=0):
        self.levels = { 'ERROR': ERROR, 'SUCCESS': SUCCESS, 'WARNING': WARNING, 'INFO': INFO, 'DEBUG': DEBUG }
        self.verbose = verbose
        self.DEBUG_LEVEL = int(debug_level)
        self.error_file = open('errors.log', 'a')
        self.log_file = open('logs.log', 'a')
        self.config = {
            'log_file': 'logs.log',
            'error_file': 'errors.log',
            'verbose': verbose,
            'debug_level': debug_level
        }

    def log(self, message, level):
        """
        Logs a message with a specified log level and handles the output based on the debug level.

        Args:
        message (str): The message to be logged.
        level (str): The log level of the message. Possible values include ERROR, SUCCESS, WARNING, INFO, etc.

        Behavior:
        - Formats the log message with a timestamp and color coding.
        - Writes the log message to either a general log file or an error log file based on the log level.
        - If verbose mode is enabled, outputs the log message to the console based on the DEBUG_LEVEL:
            DEBUG_LEVEL 0: Logs all messages.
            DEBUG_LEVEL 1: Logs only ERROR messages.
            DEBUG_LEVEL 2: Logs only SUCCESS messages.
            DEBUG_LEVEL 3: Logs only WARNING messages.
            DEBUG_LEVEL 4: Logs only INFO messages.
            DEBUG_LEVEL 5: Logs ERROR and WARNING messages.
            DEBUG_LEVEL 6: Logs INFO and SUCCESS messages.
            DEBUG_LEVEL 7: Logs ERROR, WARNING, and INFO messages.
        """

        log = f'{DEBUG} MGS Timing: \x1b[32m [ {datetime.now()} ] \x1b[0m \n{self.levels[level]} {message}\n\n'
        if (level != 'ERROR'):
            self.log_file.write(log)
            self.log_file.flush()
        else:
            self.error_file.write(log)
            self.error_file.flush()

        if self.verbose:
            if self.DEBUG_LEVEL == 0: print(log, end='')
            elif self.DEBUG_LEVEL == 1 and level == 'ERROR': print(log, end='')
            elif self.DEBUG_LEVEL == 2 and level == 'SUCCESS': print(log, end='')
            elif self.DEBUG_LEVEL == 3 and level == 'WARNING': print(log, end='')
            elif self.DEBUG_LEVEL == 4 and level == 'INFO': print(log, end='')
            elif self.DEBUG_LEVEL == 5 and (level == 'ERROR' or level == 'WARNING'): print(log, end='')
            elif self.DEBUG_LEVEL == 6 and (level == 'INFO' or level == 'SUCCESS'): print(log, end='')
            elif self.DEBUG_LEVEL == 7 and (level == 'ERROR' or level == 'WARNING' or level == 'INFO'): print(log, end='')

    def close(self):
        """
        Closes the log and error files.
        """
        self.log('Closing log files.', 'INFO')
        self.log_file.close()
        self.error_file.close()

DEBUG = '\x1b[1m[\x1b[36m DEBUG \x1b[0m\x1b[1m]\x1b[22m'
ERROR = '\x1b[1m[\x1b[31m ERROR \x1b[0m\x1b[1m]\x1b[22m'
SUCCESS = '\x1b[1m[\x1b[32m SUCCESS \x1b[0m\x1b[1m]\x1b[22m'
WARNING = '\x1b[1m[\x1b[33m WARNING \x1b[0m\x1b[1m]\x1b[22m'
INFO = '\x1b[1m[\x1b[34m INFO \x1b[0m\x1b[1m]\x1b[22m'

logger = Logger(verbose='--verbose' in sys.argv, debug_level=os.getenv('DEBUG_LEVEL', 0))