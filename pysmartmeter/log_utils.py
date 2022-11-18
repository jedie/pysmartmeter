import atexit
import logging
import tempfile


def logger_setup(*, logger_name, level, format, log_filename):
    logger = logging.getLogger(logger_name)
    is_configured = logger.handlers and logger.level
    if not is_configured:
        logger.setLevel(level)

        if log_filename:
            ch = logging.FileHandler(filename=log_filename)
        else:
            ch = logging.StreamHandler()
        ch.setLevel(level)
        ch.setFormatter(logging.Formatter(format))

        logger.addHandler(ch)


def print_log_info(filename):
    print(f'\nLog file created here: {filename}\n')


def log_config(
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s %(name)s.%(funcName)s %(lineno)d | %(message)s',
    log_in_file=True,
):
    if log_in_file:
        log_file = tempfile.NamedTemporaryFile(prefix='pysmartmeter_', suffix='.log', delete=False)
        log_filename = log_file.name
    else:
        log_filename = None

    logger_setup(
        logger_name='pysmartmeter',
        level=level,
        format=format,
        log_filename=log_filename,
    )

    if log_filename:
        atexit.register(print_log_info, log_filename)


def log_func_call(*, logger, func, **kwargs):
    func_name = func.__name__
    logger.debug('Call %r with: %r', func_name, kwargs)
    result = func(**kwargs)
    logger.debug('%r result: %r', func_name, result)
    return result
