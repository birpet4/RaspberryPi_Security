import logging
from raspberry_sec.interface.action import Action


class TestAction(Action):

    LOGGER = logging.getLogger('TestAction')

    def get_name(self):
        return 'TestAction'

    def fire(self, msg: str):
        TestAction.LOGGER.info('Action fired: ' + msg)
