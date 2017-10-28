import cv2
from raspberry_sec.module.facedetector.consumer import FacedetectorConsumer, ConsumerContext


def set_parameters():
	parameters = dict()
	parameters['cascade_file'] = 'resource/haarcascade_frontalface_default.xml'
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
		while cv2.waitKey(50) != 10:
			success, frame = cap.read()
			if success:
				context.data = frame
				consumer.run(context)
			if context.alert:
				print('Face Detected')
				cv2.imshow('Face', context.data)
	finally:
		cap.release()
		cv2.destroyAllWindows()


if __name__ == '__main__':
	integration_test()
