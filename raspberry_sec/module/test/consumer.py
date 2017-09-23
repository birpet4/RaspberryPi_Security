import time
import logging
from raspberry_sec.interface.producer import Type
from raspberry_sec.interface.consumer import Consumer, ConsumerContext


class TestConsumer(Consumer):

    LOGGER = logging.getLogger('TestConsumer')

    def get_name(self):
        return 'TestConsumer'

    def run(self, context: ConsumerContext):
        if context.alert:
            TestConsumer.LOGGER.info('Sleeping now')
            time.sleep(5)
            TestConsumer.LOGGER.debug('Finished sleeping')
            return context
        else:
            return ConsumerContext('data', False)

    def get_type(self):
        return Type.CAMERA
