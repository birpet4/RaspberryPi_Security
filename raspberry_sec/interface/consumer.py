class ConsumerContext:

    def __init__(self, _data, _alert: bool):
        self.data = _data
        self.alert = _alert
        
        
class Consumer:
    
    def get_name(self):
        pass

    def run(self, context: ConsumerContext):
        pass

    def get_type(self):
        pass
    
    def __eq__(self, other):
        return self.get_name() == other.get_name()

    def __hash__(self):
        return hash(self.get_name())
