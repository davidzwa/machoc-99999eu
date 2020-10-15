import logging

from base_gui.utils.color import style

LOG_FORMAT = ('%(levelname) -10s %(asctime)s %(name) -15s %(funcName) '
              '-10s %(lineno) -5d: %(message)s')

LOGGER = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)


def log_main(*args, style_formatter=style.WHITE):
    if callable(style_formatter):
        LOGGER.warning(style_formatter(args))


def log_child(*args, style_formatter=style.CYAN):
    if callable(style_formatter):
        LOGGER.warning(style_formatter(args))
