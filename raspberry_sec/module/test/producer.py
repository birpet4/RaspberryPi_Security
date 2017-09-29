import logging
import time
from raspberry_sec.interface.producer import Producer, Type


class TestProducer(Producer):
    """
    Producer class for testing purposes
    """
    LOGGER = logging.getLogger('TestProducer')

    def get_name(self):
        return 'TestProducer'

    def get_data(self):
        TestProducer.LOGGER.info('Producer called')
        time.sleep(0.5)
        return 'TestProducer data'

    def get_type(self):
    	return Type.CAMERA
