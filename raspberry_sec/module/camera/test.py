import cv2


def system_test():
	# Given
	title = 'Camera Test'

	# When
	try:
		cap = cv2.VideoCapture(0)
		while cv2.waitKey(50) != 10:
			_, frame = cap.read()
			cv2.imshow(title, frame)
	finally:
		cap.release()
		cv2.destroyAllWindows()


if __name__ == '__main__':
	system_test()
