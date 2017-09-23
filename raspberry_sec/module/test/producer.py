import logging
from raspberry_sec.interface.producer import Producer, Type


class TestProducer(Producer):

    LOGGER = logging.getLogger('TestProducer')

    def get_name(self):
        return 'TestProducer'

    def get_data(self):
        TestProducer.LOGGER.info('Producer called')
        return 'TestProducer data'

    def get_type(self):
        return Type.CAMERA
