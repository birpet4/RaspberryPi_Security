import logging
import time
from raspberry_sec.interface.producer import Type
from raspberry_sec.interface.consumer import Consumer, ConsumerContext


class MotiondetectorConsumer(Consumer):
	"""
	Consumer class for detecting motion
	"""
	LOGGER = logging.getLogger('MotiondetectorConsumer')

	def __init__(self, parameters: dict):
		"""
		Constructor
		:param parameters: see Consumer constructor
		"""
		super().__init__(parameters)
		self.previous_frame = None

	def get_name(self):
		return 'MotiondetectorConsumer'

	def run(self, context: ConsumerContext):
		import cv2

		img = context.data
		context.alert = False

		if img is None:
			MotiondetectorConsumer.LOGGER.debug('No image')
			time.sleep(self.parameters['timeout'])
			return context

		frame = cv2.resize(img, (self.parameters['resize_width'], self.parameters['resize_height']))
		gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
		gray = cv2.GaussianBlur(gray, (21, 21), 0)

		# if the first frame is None, initialize it
		if self.previous_frame is None:
			self.previous_frame = gray
			return context

		# compute the absolute difference between the current frame and previous frame
		frame_delta = cv2.absdiff(self.previous_frame, gray)
		(_, thresh) = cv2.threshold(src=frame_delta,
									thresh=self.parameters['threshold'],
									maxval=self.parameters['threshold_max_val'],
									type=cv2.THRESH_BINARY)

		# dilate the image to fill in holes, then find contours on image
		thresh = cv2.dilate(thresh, None, iterations=self.parameters['dilate_iteration'])
		(_, contours, _) = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

		# loop over the contours
		motion_detected = any([True for c in contours if cv2.contourArea(c) > self.parameters['area_threshold']])
		if motion_detected:
			context.alert = True
			context.alert_data = 'Motion detected'
			MotiondetectorConsumer.LOGGER.debug(context.alert_data)
		else:
			MotiondetectorConsumer.LOGGER.debug('No motion was detected')

		self.previous_frame = gray
		return context

	def get_type(self):
		return Type.CAMERA
