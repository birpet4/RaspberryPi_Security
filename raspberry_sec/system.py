import time
import logging
from concurrent.futures import ThreadPoolExecutor
from raspberry_sec.interface.producer import Producer
from raspberry_sec.interface.consumer import Consumer, ConsumerContext
from raspberry_sec.interface.action import Action


class Stream:

    LOGGER = logging.getLogger('Stream')

    def __init__(self):
        self.producer = None
        self.consumers = []
        self.enabled = True
        self.stream_controller = None

    def validate(self):
        pass

    def run(self):
        while self.enabled:
            data = self.producer.get_data()
            
            context = ConsumerContext(data, True)
            for consumer in self.consumers:
                context = consumer.run(context)
            
            self.stream_controller.set_alert(self, context.alert)


class StreamController:

    LOGGER = logging.getLogger('StreamController')

    def __init__(self):
        self.stream_alerts = {}
        self.enabled = True

    def set_alert(self, stream: Stream, alert: bool):
        self.stream_alerts[stream] = alert 

    def run(self):
        while self.enabled:
            time.sleep(3)
            alert = all(self.stream_alerts.values())
            if alert:
                self.LOGGER.info('ALERT !!!')


class PCASystem:

    LOGGER = logging.getLogger('PCASystem')

    def __init__(self):
        self.producers = set()
        self.consumers = set()
        self.actions = set()
        self.streams = set()
        self.stream_controller = None

    def validate(self):
        pass

    def run(self):
        stream_thread_count = len(self.streams)
        futures = []

        if stream_thread_count:
            with ThreadPoolExecutor(max_workers=stream_thread_count) as executor:
                for stream in self.streams:
                    futures.append(executor.submit(stream.run))

            self.stream_controller.run()

            for future in futures:
                future.cancel()
            executor.shutdown()
        else:
            self.LOGGER.error('No streams defined')
