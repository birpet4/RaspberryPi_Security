import logging
import re
import time
import pickle
import os, sys, json
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
from concurrent.futures import ThreadPoolExecutor
from itertools import groupby

LOGGER = logging.getLogger('ZoneManager') 
zones = None


@staticmethod
def get_abs_path(file: str):
        """
        :return: the absolute path to file
        """
        return os.path.abspath(os.path.join(os.path.dirname(__file__), file))

CONFIG_PATH = get_abs_path.__func__('../../config/prod/pca_system.json')

def initialize():
	"""
	Function for inizializing the zone manager module
	:param _zones: the zones coming from the html code
	"""
	LOGGER.info('Initializing ZoneManager...')
	with open(CONFIG_PATH, 'r') as file:
		config = file.read()

	data = json.loads(config)
	stream_controller = data['stream_controller']
	zones = stream_controller['zones'] 

	if zones:
		print(zones)
		LOGGER.info('ZoneManager inizialized')
	else:
		LOGGER.info('Error initializing ZoneManager')

def set_zones(_zones: str):
	"""
	"""
	LOGGER.info('Loading ZoneManager...')
	with open(CONFIG_PATH, 'r') as file:
		config = file.read()

	data = json.loads(config)
	stream_controller = data['stream_controller']
	zones = stream_controller['zones'] 
	data['stream_controller']['zones'] = _zones
	print(data)
	new_config = json.dumps(data)
	print(new_config)
	with open(CONFIG_PATH, 'w+') as file:
		json.dump(fp=file, obj=data, indent=4, sort_keys=True)
                #file.write(new_config)

def get_zones():
	"""
	Function for get available zones
	return: dictionary of zones
	"""
	with open(CONFIG_PATH, 'r') as file:
		config = file.read()

	data = json.loads(config)
	stream_controller = data['stream_controller']
	zones = stream_controller['zones'] 
	
	return zones

def is_zone_active(zone: str):
	"""
	Function for deciding whether zone is active or not
	:param zone: zone, from which we want to know whether active or not
	"""
	with open(CONFIG_PATH, 'r') as file:
		config = file.read()

	data = json.loads(config)
	stream_controller = data['stream_controller']
	zones = stream_controller['zones'] 

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
	with open(CONFIG_PATH, 'r') as file:
		config = file.read()

	data = json.loads(config)
	stream_controller = data['stream_controller']
	zones = stream_controller['zones'] 

	for key, value in zones.items():
			if key == zone:
				zones[key] = not value
				LOGGER.info('Toggle ' + zone + ' activity')
				"""pickle.dump(zones, open('zone.pkl','wb'))"""
				with open(CONFIG_PATH, 'w') as file:
					file.write(new_config)

