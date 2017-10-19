import cv2
import time


def integration_test():
	# Given
	time.sleep(1)
	previous_frame = None
	THRESHOLD = 25
	THRESH_MAX_VAL = 255
	DILATE_ITERATION = 2
	AREA_THRESHOLD = 250
	RESIZE = (320, 240)

	# When
	try:
		camera = cv2.VideoCapture(0)

		while cv2.waitKey(100) != 10:
			# grab the current frame and initialize the occupied/unoccupied
			(grabbed, frame) = camera.read()

			frame = cv2.resize(frame, RESIZE)
			gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
			gray = cv2.GaussianBlur(gray, (21, 21), 0)

			# if the first frame is None, initialize it
			if previous_frame is None:
				previous_frame = gray
				continue

			# compute the absolute difference between the current frame and previous frame
			frame_delta = cv2.absdiff(previous_frame, gray)
			(_, thresh) = cv2.threshold(src=frame_delta,
										thresh=THRESHOLD,
										maxval=THRESH_MAX_VAL,
										type=cv2.THRESH_BINARY)

			# dilate the thresholded image to fill in holes, then find contours on thresholded image
			thresh = cv2.dilate(thresh, None, iterations=DILATE_ITERATION)
			(_, contours, _) = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

			# loop over the contours
			motion_detected = any([True for c in contours if cv2.contourArea(c) > AREA_THRESHOLD])
			print(motion_detected)

			previous_frame = gray

			cv2.imshow('Thresh', thresh)
	finally:
		camera.release()
		cv2.destroyAllWindows()


if __name__ == '__main__':
	integration_test()
