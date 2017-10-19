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
	WIN_STRIDE = (4, 4)
	PADDING = (16, 16)
	SCALE = 1.23
	RESIZE = (320, 240)

	# When
	try:
		cap = cv2.VideoCapture(0)

		while cv2.waitKey(100) != 10:
			_, frame = cap.read()
			resized_frame = cv2.resize(frame, RESIZE)
			grey_image = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2GRAY)
			found, w = hog.detectMultiScale(grey_image, winStride=WIN_STRIDE, padding=PADDING, scale=SCALE)
			if len(found) > 0:
				print('Detected')

			draw_detections(grey_image, found)

			cv2.imshow('feed', grey_image)
	finally:
		cap.release()
		cv2.destroyAllWindows()


if __name__ == '__main__':
	integration_test()
