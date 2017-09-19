class Action:

    def get_name(self):
        pass

    def fire(self, msg: str):
        pass
    
    def __eq__(self, other):
        return self.get_name() == other.get_name()

    def __hash__(self):
        return hash(self.get_name())