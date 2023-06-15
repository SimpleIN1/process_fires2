import functools
import logging
import pathlib
import datetime
import time
import traceback


def error_wraps(func):

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger = Log('logs')
        try:
            result = func(*args, **kwargs)
            return result
        except Exception as e:
            # response = {
            #     'func': func.__name__,
            #     'message': e,
            # }
            response = traceback.format_exc()

            logger.logger.error(
                response
            )
            # print(response)
    return wrapper


class Log:
    def __init__(self, dir):
        self.make_dir(dir)
        logging.basicConfig(
            level=logging.INFO,
            filename=f'{dir}/logs_{datetime.datetime.now().strftime("%Y%m%d")}.log',
            filemode='a',
            format="%(asctime)s %(levelname)s %(message)s",
        )

        logging.getLogger().addHandler(
            logging.StreamHandler()
        )
        self.logger = logging.getLogger('LoggerName')

    def make_dir(self, dirname) -> None:
        pathlib.Path(dirname).mkdir(parents=True, exist_ok=True)
