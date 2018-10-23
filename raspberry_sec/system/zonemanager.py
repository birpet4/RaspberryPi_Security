import logging
import re
import time
import pickle
from concurrent.futures import ThreadPoolExecutor
from itertools import groupby

LOGGER = logging.getLogger('ZoneManager') 
zones = None

def initialize(_zones: dict):
	"""
	Function for inizializing the zone manager module
	:param _zones: the zones coming from the html code
	"""
	LOGGER.info('Initializing ZoneManager...')
	zones = _zones
	pickle.dump(zones, open('zone.pkl','wb'))
	if zones:
		print(zones)
		LOGGER.info('ZoneManager inizialized')
	else:
		LOGGER.info('Error initializing ZoneManager')


def get_zones():
	"""
	Function for get available zones
	return: dictionary of zones
	"""
	return pickle.load(open('zone.pkl','rb'))

def is_zone_active(zone: str):
	"""
	Function for deciding whether zone is active or not
	:param zone: zone, from which we want to know whether active or not
	"""
	zones = pickle.load(open('zone.pkl','rb'))
	for key, value in zones.items():
		if key == zone and zones[key] == True:
			LOGGER.info(zone + ' is active')
			return True
	LOGGER.info(zone + ' is inactive, not alert')
	return False


def toggle_zone(zone: str):
	"""
	Function for toggle zone activity
	:param zone: the actual zone what we want to activate or deactivate
	"""
	zones = pickle.load(open('zone.pkl','rb'))
	for key, value in zones.items():
			if key == zone:
				zones[key] = not value
				LOGGER.info('Toggle ' + zone + ' activity')
				pickle.dump(zones, open('zone.pkl','wb'))

