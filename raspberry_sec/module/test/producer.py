from raspberry_sec.interface.producer import Producer


class TestProducer(Producer):

    def get_name(self):
        return 'TestProducer'

    def get_data(self):
        print('Producer called')
        return 'TestProducer data'