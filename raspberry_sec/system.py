import time
from concurrent.futures import ThreadPoolExecutor
from raspberry_sec.interface.producer import Producer
from raspberry_sec.interface.consumer import Consumer, ConsumerContext
from raspberry_sec.interface.action import Action


class StreamController:

    def __init__(self):
        self.stream_alerts = {}
        self.enabled = True

    def set_alert(self, stream: Stream, alert: bool)
        self.stream_alerts[stream] = alert 

    def run(self):
        while enabled:
            time.sleep(3)
            alert = all(self.stream_alerts.values())
            if alert:
                print('ALERT !!!')


class Stream:

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


class PCASystem:

    def __init__(self):
        self.producers = set()
        self.consumers = set()
        self.actions = set()
        self.streams = set()
        self.stream_controller = None

    def validate(self):
        pass

    def run(self):
        thread_count = len(streams) + 1
        futures = []
        with ThreadPoolExecutor(max_workers=thread_count) as executor:
            futures.append(executor.submit(self.stream_controller.run))
            for stream in self.streams:
                futures.append(executor.submit(stream.run))

        time.sleep(22)
        for future in futures:
            future.cancel()
        executor.shutdown()