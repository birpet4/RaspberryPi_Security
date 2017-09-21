from raspberry_sec.interface.action import Action


class TestAction(Action):

    def get_name(self):
        return 'TestAction'

    def fire(self, msg: str):
        print('Action fired: ' + msg)
