import logging
import re
import time
import pickle
from concurrent.futures import ThreadPoolExecutor
from itertools import groupby

LOGGER = logging.getLogger('ZoneManager') 
zones = None

def initialize(_zones: dict):

	LOGGER.info('Initializing ZoneManager...')
	zones = _zones
	print(zones)
	print(_zones)
	pickle.dump(zones, open('zone.pkl','wb'))
	if zones:
		print(zones)
		LOGGER.info('ZoneManager inizialized')
	else:
		LOGGER.info('Error initializing ZoneManager')


def get_zones():
	global zones
	return pickle.load(open('zone.pkl','rb'))

def validate(self):
	"""
	This method validates whether zones is properly configured.
	Raises exception if not.
	:return True if it seems to be alright
	"""
	if self.zones is None:
		msg = 'No producer set for stream: ' + self.name
		ZoneManager.LOGGER.error(msg)
		raise AttributeError(msg)
		return True

def is_zone_active(self, zone: str):
	zones = pickle.load(open('zone.pkl','rb'))
	for key, value in zones.items():
		if key == zone and zones[key] == True:
			return True
	return False


def print_zones(self):
	""" 
	print available zones 
	"""
	zone_names = list(self.zones.keys())
	for x in range(len(self.zones)):
		print(zone_names[x])

def toggle_zone(zone: str):
	"""
	This method toggle zone activity //TODO
	"""
	zones = pickle.load(open('zone.pkl','rb'))
	for key, value in zones.items():
			if key == zone:
				zones[key] = not value
				pickle.dump(zones, open('zone.pkl','wb'))
def run(self):
	print('semmi')


