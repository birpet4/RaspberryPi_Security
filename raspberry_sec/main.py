import os
import sys
import logging
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))


LOGGER = logging.getLogger('main')


def setup_logging():
    logging.basicConfig(
        format='[%(asctime)s]:%(name)s:%(levelname)s - %(message)s',
        level=logging.DEBUG)


def main():
    setup_logging()
    LOGGER.info('Starting up service')


if __name__ == '__main__':
    main()
