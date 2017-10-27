import cv2
import numpy as np


def integration_test():
	# Given
	face_cascade = cv2.CascadeClassifier('resource/haarcascade_frontalface_default.xml')

	SCALE_FACTOR = 1.3
	MIN_NEIGHBORS = 5

	# When
	try:
		cap = cv2.VideoCapture(0)
		crop = np.zeros((300, 300, 3), np.uint8)

		while cv2.waitKey(100) != 10:
			_, frame = cap.read()
			grey_image = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
			faces = face_cascade.detectMultiScale(image=grey_image, scaleFactor=SCALE_FACTOR, minNeighbors=MIN_NEIGHBORS)

			if len(faces):
				(x, y, w, h) = faces[0]
				crop = grey_image[y:y + h, x:x + w]

			cv2.imshow('Face', crop)
	finally:
		cap.release()
		cv2.destroyAllWindows()


if __name__ == '__main__':
	integration_test()
