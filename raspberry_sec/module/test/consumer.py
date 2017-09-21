import time
from raspberry_sec.interface.consumer import Consumer, ConsumerContext


class TestConsumer(Consumer):
    
    def get_name(self):
        return 'TestConsumer'

    def run(self, context: ConsumerContext):
        if context.alert:
            print('Sleeping now')
            time.sleep(5)
            print('Finished sleeping')
            return context
        else:
            return ConsumerContext('data', False)
