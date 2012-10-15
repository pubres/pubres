import logging

# This module is redundantly called pubres_logging
# to not conflict with the stdlib logging module.


# The official logger name of pubres.
PUBRES_LOGGER_NAME = 'pubres'


def setup_logging(level):
    # Check if the log level string is one defined in logging
    numeric_level = getattr(logging, level.upper())
    if not isinstance(numeric_level, int):
        raise ValueError('Invalid log level: %s' % level)

    ## Logger, handler and formatter

    logger = logging.getLogger(PUBRES_LOGGER_NAME)
    logger.setLevel(numeric_level)

    handler = logging.StreamHandler()
    handler.setLevel(numeric_level)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    logger.addHandler(handler)
