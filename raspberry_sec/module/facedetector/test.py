import cv2
import sys
import os
sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))
from raspberry_sec.module.facedetector.consumer import FacedetectorConsumer, ConsumerContext


def set_parameters():
	parameters = dict()
	parameters['cascade_file'] = 'resources/haarcascade_frontalface_default.xml'
	parameters['min_neighbors'] = 5
	parameters['scale_factor'] = 1.3
	parameters['timeout'] = 1
	return parameters


def integration_test():
	# Given
	consumer = FacedetectorConsumer(set_parameters())
	context = ConsumerContext(None, False)
	cap = cv2.VideoCapture(0)

	# When
	try:
		count = 0
		while cv2.waitKey(50) == -1:
			success, frame = cap.read()
			if success:
				context.data = frame
				consumer.run(context)
			if context.alert:
				print('Face Detected: ' + str(count))
				count += 1
				cv2.imshow('Face', context.data)
	finally:
		cap.release()
		cv2.destroyAllWindows()


if __name__ == '__main__':
	integration_test()
