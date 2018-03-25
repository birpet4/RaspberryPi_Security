import cv2
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))
from raspberry_sec.interface.consumer import ConsumerContext
from raspberry_sec.module.bodydetector.consumer import BodydetectorConsumer


def set_parameters():
	parameters = dict()
	parameters['padding_x'] = 8
	parameters['padding_y'] = 8
	parameters['resize_height'] = 240
	parameters['resize_width'] = 320
	parameters['scale'] = 1.15
	parameters['timeout'] = 1
	parameters['win_stride_x'] = 4
	parameters['win_stride_y'] = 4
	return parameters


def integration_test():
	# Given
	parameters = set_parameters()
	consumer = BodydetectorConsumer(parameters)
	context = ConsumerContext(None, False)
	cap = cv2.VideoCapture(0)

	# When
	try:
		count = 0
		while cv2.waitKey(100) == -1:
			success, frame = cap.read()
			if success:
				context.data = cv2.resize(frame, (parameters['resize_width'], parameters['resize_height']))
				consumer.run(context)
			if context.alert:
				cv2.imshow('Frame', context.data)
				print('Detected: ' + str(count))
				count += 1
	finally:
		cap.release()
		cv2.destroyAllWindows()


if __name__ == '__main__':
	integration_test()
