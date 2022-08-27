# pylint: disable=line-too-long
"""
Logging Module
"""
import logging
import sys
import inspect
import traceback
from logging import DEBUG


class Logs:
    """Logging class"""

    format = "[%(asctime)s]-[%(levelname)s]-[%(function)s] : [%(message)s]"
    format_date = "%Y-%m-%d %H:%M:%S"
    console_formatter = logging.Formatter(format, datefmt=format_date)
    console_logger = logging.StreamHandler(sys.stdout)
    console_logger.setFormatter(console_formatter)
    logger = logging.getLogger("pixitrend")
    logger.setLevel(level=DEBUG)
    logger.addHandler(console_logger)
    log_file = logging.FileHandler("logs.log")
    log_file.setFormatter(console_formatter)
    logger.addHandler(log_file)

    def __init__(self, level=DEBUG):
        self.extra = {}
        self.level = level

    def info(self, msg):
        """INFO override function"""
        self.set_function_name()
        self.logger.info(msg, extra=self.extra)

    def error(self, msg):
        """ERROR override function"""
        self.set_function_name()
        _, _, tba = sys.exc_info()
        filename, lineno, funname, line = traceback.extract_tb(tba)[-1]
        debug = f"Filename = {filename} -- Line = {lineno} -- function = {funname} -- codeline = {line}"
        self.logger.error(f"{debug} -- msg = {msg}", extra=self.extra)

    def debug(self, msg):
        """DEBUG override function"""
        self.set_function_name()
        self.logger.debug(msg, extra=self.extra)

    def warn(self, msg):
        """WARN override function"""
        self.set_function_name()
        self.logger.warning(msg, extra=self.extra)

    def set_function_name(self):
        """Set the caller function"""
        # Get call function's name
        func = inspect.currentframe().f_back.f_back.f_code
        self.extra["function"] = func.co_name
