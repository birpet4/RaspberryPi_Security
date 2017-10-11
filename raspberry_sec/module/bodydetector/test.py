import cv2


def draw_detections(img, rectangles, thickness=1):
	"""
	Draws green rectangles around the bodies HOG found
	:param img: we want to draw in
	:param rectangles: found by HOG
	:param thickness: of the rectangles
	"""
	for x, y, w, h in rectangles:
		cv2.rectangle(
			img,
			(x, y),
			(x + w, y + h),
			(0, 255, 0),
			thickness)


def integration_test():
	# Given
	hog = cv2.HOGDescriptor()
	hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

	# When
	try:
		cap = cv2.VideoCapture(0)
		while cv2.waitKey(50) != 10:
			_, frame = cap.read()

			found, w = hog.detectMultiScale(frame, winStride=(8, 8), padding=(32, 32), scale=1.05)
			if len(found) > 0:
				print('Detected')

			draw_detections(frame, found)

			cv2.imshow('feed', frame)
	finally:
		cap.release()
		cv2.destroyAllWindows()


if __name__ == '__main__':
	integration_test()
