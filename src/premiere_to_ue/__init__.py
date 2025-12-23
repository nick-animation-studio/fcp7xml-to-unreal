"""Process editorial XML from Adobe Premiere for import into Unreal Engine."""

import importlib.metadata
import logging
import os
import yaml

__version__ = importlib.metadata.version(__package__)

config = {}


def setup_logger(log_level: str = "INFO") -> logging.Logger:
    """
    Configure and return a logger instance.
    """
    logger = logging.getLogger(__name__)
    logger.setLevel(log_level)

    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)

    if log_level == "DEBUG":
        # Create detailed formatter for debug log messages
        formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] %(name)s: %(filename)s:%(lineno)d - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    elif log_level == "ERROR":
        # Create formatter for error log messages
        formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    else:
        # Default to simple formatter for info and warning log messages
        formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
        )
    console_handler.setFormatter(formatter)

    # Avoid adding multiple handlers if logger already configured
    if not logger.handlers:
        logger.addHandler(console_handler)

    return logger


log_level = os.getenv("LOGLEVEL", "INFO").upper()

logger = setup_logger(log_level=log_level)

with open(os.path.join(os.path.dirname(__file__), "config.yaml")) as file:
    internal_config = yaml.safe_load(file)
    logger.info("using internal config.yaml.")
    config = internal_config

# optional local config, when found in current directory
if os.path.isfile("config.yaml"):
    with open("config.yaml") as local_file:
        logger.info("using additional local config.yaml.")
        local_config = yaml.safe_load(local_file)
        config = internal_config | local_config

logger.debug(f"using config: {config}")
