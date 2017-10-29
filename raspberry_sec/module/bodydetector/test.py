import cv2
from raspberry_sec.interface.consumer import ConsumerContext
from raspberry_sec.module.bodydetector.consumer import BodydetectorConsumer


def set_parameters():
	parameters = dict()
	parameters['padding_x'] = 16
	parameters['padding_y'] = 16
	parameters['resize_height'] = 360
	parameters['resize_width'] = 640
	parameters['scale'] = 1.23
	parameters['timeout'] = 1
	parameters['win_stride_x'] = 4
	parameters['win_stride_y'] = 4
	return parameters


def integration_test():
	# Given
	consumer = BodydetectorConsumer(set_parameters())
	context = ConsumerContext(None, False)
	cap = cv2.VideoCapture(0)

	# When
	try:
		while cv2.waitKey(100) == -1:
			success, frame = cap.read()
			if success:
				context.data = cv2.resize(frame, (640, 360))
				consumer.run(context)
			if context.alert:
				cv2.imshow('Frame', context.data)
				print('Detected')
	finally:
		cap.release()
		cv2.destroyAllWindows()


if __name__ == '__main__':
	integration_test()
