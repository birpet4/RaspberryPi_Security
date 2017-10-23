import cv2
import os
import numpy as np


def eigen_integration_test(labels_with_images: dict, names_with_labels: dict):
	print('Training samples must be of equal size')


def fisher_integration_test(labels_with_images: dict, names_with_labels: dict):
	print('Training samples must be of equal size')


def lbp_integration_test(labels_with_images: dict, names_with_labels: dict):
	recognizer = cv2.face.LBPHFaceRecognizer_create()

	images = []
	labels = []
	for key, value in labels_with_images.items():
		images += value
		labels += [key for _ in range(len(value))]

	recognizer.train(images, np.array(labels))

	try:
		cap = cv2.VideoCapture(0)
		face = None
		while face is None:
			_, img = cap.read()
			face = detect_face(img)

		label, confidence = recognizer.predict(face)
		name = str({key for key, value in names_with_labels.items() if value == label})
		print('Prediction: ' + name + ' with confidence: ' + str(confidence))
	finally:
		cap.release()


def get_images_and_labels(path):
	labels_with_images = {}
	names_with_labels = {}
	image_paths = []

	for root, dirs, files in os.walk(path):
		image_paths += [os.sep.join([root, file]) for file in files if file.endswith('.png')]

	global_label = 0
	for image_path in image_paths:
		image = cv2.imread(image_path)
		name = os.path.split(image_path)[1].split('.')[0]

		if not names_with_labels.__contains__(name):
			names_with_labels[name] = global_label
			labels_with_images[global_label] = []
			global_label += 1

		face = detect_face(image)
		if face is not None:
			label = names_with_labels[name]
			labels_with_images[label] += [face]
			cv2.imshow('Adding face to traning set...', face)
			cv2.waitKey(10)

	return labels_with_images, names_with_labels


def detect_face(img):
	face_cascade = cv2.CascadeClassifier('resource/haarcascade_frontalface_default.xml')
	SCALE_FACTOR = 1.3
	MIN_NEIGHBORS = 5

	grey_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
	faces = face_cascade.detectMultiScale(image=grey_image, scaleFactor=SCALE_FACTOR, minNeighbors=MIN_NEIGHBORS)

	if len(faces):
		(x, y, w, h) = faces[0]
		return grey_image[y:y + h, x:x + w]
	else:
		return None


def produce_face_data():
	WHO = 'simon'
	SAVE_TO = 'training_data/' + WHO + '/'
	TIMEOUT = 5000

	try:
		cap = cv2.VideoCapture(0)
		crop = np.zeros((300, 300, 3), np.uint8)
		count = -1

		while cv2.waitKey(TIMEOUT) != 10:
			_, frame = cap.read()
			if frame is not None:
				face = detect_face(frame)
				if face is not None:
					crop = face
					count += 1
					cv2.imwrite(filename=SAVE_TO + WHO + '.' + str(count) + '.png', img=crop)
			cv2.imshow('Face', crop)
	finally:
		cap.release()
		cv2.destroyAllWindows()


if __name__ == '__main__':
	path = 'training_data'
	labels_with_images, names_with_labels = get_images_and_labels(path)

	lbp_integration_test(labels_with_images, names_with_labels)
	#eigen_integration_test(labels_with_images, names_with_labels)
	#fisher_integration_test(labels_with_images, names_with_labels)
