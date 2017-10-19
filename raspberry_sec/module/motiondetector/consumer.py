import logging
import time
from raspberry_sec.interface.producer import Type
from raspberry_sec.interface.consumer import Consumer, ConsumerContext


class MotiondetectorConsumer(Consumer):
	"""
	Consumer class for detecting motion
	"""
	LOGGER = logging.getLogger('MotiondetectorConsumer')
	THRESHOLD = 25
	THRESH_MAX_VAL = 255
	DILATE_ITERATION = 2
	AREA_THRESHOLD = 250
	RESIZE = (320, 240)

	def __init__(self):
		"""
		Constructor
		"""
		self.previous_frame = None

	def get_name(self):
		return 'MotiondetectorConsumer'

	def run(self, context: ConsumerContext):
		import cv2

		img = context.data
		context.alert = False

		if img is None:
			MotiondetectorConsumer.LOGGER.debug('No image')
			return context

		frame = cv2.resize(img, MotiondetectorConsumer.RESIZE)
		gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
		gray = cv2.GaussianBlur(gray, (21, 21), 0)

		# if the first frame is None, initialize it
		if self.previous_frame is None:
			self.previous_frame = gray
			return context

		# compute the absolute difference between the current frame and previous frame
		frame_delta = cv2.absdiff(self.previous_frame, gray)
		(_, thresh) = cv2.threshold(src=frame_delta,
									thresh=MotiondetectorConsumer.THRESHOLD,
									maxval=MotiondetectorConsumer.THRESH_MAX_VAL,
									type=cv2.THRESH_BINARY)

		# dilate the thresholded image to fill in holes, then find contours on thresholded image
		thresh = cv2.dilate(thresh, None, iterations=MotiondetectorConsumer.DILATE_ITERATION)
		(_, contours, _) = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

		# loop over the contours
		motion_detected = any([True for c in contours if cv2.contourArea(c) > MotiondetectorConsumer.AREA_THRESHOLD])
		if motion_detected:
			context.alert = True
			MotiondetectorConsumer.LOGGER.info('Motion detected')

		return context

	def get_type(self):
		return Type.CAMERA
