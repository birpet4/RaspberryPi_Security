import cv2
import os
import numpy as np


def integration_test(labels_with_images: dict, names_with_labels: dict, size: int, path: str):
	eigen_recognizer = cv2.face.EigenFaceRecognizer_create(num_components=10, threshold=4000.0)
	fisher_recognizer = cv2.face.FisherFaceRecognizer_create(num_components=5, threshold=600.0)
	lbph_recognizer = cv2.face.LBPHFaceRecognizer_create(radius=3, neighbors=9, grid_x=7, grid_y=7, threshold=80.0)

	file = os.sep.join([path, 'eigen.yml'])
	if os.path.exists(file):
		eigen_recognizer.load(file)
	else:
		train_recognizer(labels_with_images, eigen_recognizer, file)

	file = os.sep.join([path, 'fisher.yml'])
	if os.path.exists(file):
		fisher_recognizer.load(file)
	else:
		train_recognizer(labels_with_images, fisher_recognizer, file)

	file = os.sep.join([path, 'lbph.yml'])
	if os.path.exists(file):
		lbph_recognizer.load(file)
	else:
		train_recognizer(labels_with_images, lbph_recognizer, file)

	try:
		cap = cv2.VideoCapture(0)
		while True:
			_, frame = cap.read()
			img = detect_face(frame)
			if img is not None:
				img = resize_image(img, size)

				e_label, e_confidence = eigen_recognizer.predict(img)
				f_label, f_confidence = fisher_recognizer.predict(img)
				l_label, l_confidence = lbph_recognizer.predict(img)

				e_name = {key for key, value in names_with_labels.items() if value == e_label}
				f_name = {key for key, value in names_with_labels.items() if value == f_label}
				l_name = {key for key, value in names_with_labels.items() if value == l_label}

				text = 'Eigen: '
				if 0 == len(e_name):
					text += 'Cannot identify the face'
					cv2.putText(img, text, (5, 5), cv2.FONT_HERSHEY_SIMPLEX, 0.25, (255, 0, 0), 1)
				else:
					text = 'Eigen: ' + e_name.pop() + ' - ' + str(e_confidence)
					cv2.putText(img, text, (5, 5), cv2.FONT_HERSHEY_SIMPLEX, 0.25, (255, 0, 0), 1)

				text = 'Fisher: '
				if 0 == len(f_name):
					text += 'Cannot identify the face'
					cv2.putText(img, text, (5, 15), cv2.FONT_HERSHEY_SIMPLEX, 0.25, (255, 0, 0), 1)
				else:
					text = 'Fisher: ' + f_name.pop() + ' - ' + str(f_confidence)
					cv2.putText(img, text, (5, 15), cv2.FONT_HERSHEY_SIMPLEX, 0.25, (255, 0, 0), 1)

				text = 'LBPH: '
				if 0 == len(l_name):
					text += 'Cannot identify the face'
					cv2.putText(img, text, (5, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.25, (255, 0, 0), 1)
				else:
					text += l_name.pop() + ' - ' + str(l_confidence)
					cv2.putText(img, text, (5, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.25, (255, 0, 0), 1)

				cv2.imshow('Recognition', img)
			cv2.waitKey(10)
	finally:
		cap.release()
		cv2.destroyAllWindows()


def get_images_and_labels(_path: str, _size: int):
	labels_with_images = {}
	names_with_labels = {}
	image_paths = []

	for root, dirs, files in os.walk(_path):
		image_paths += [os.sep.join([root, file]) for file in files if file.endswith('.png')]

	global_label = 0
	try:
		for image_path in image_paths:
			image = cv2.imread(image_path)
			name = os.path.split(image_path)[1].split('.')[0]

			if not names_with_labels.__contains__(name):
				names_with_labels[name] = global_label
				labels_with_images[global_label] = []
				global_label += 1

			f = detect_face(image)
			if f is not None:
				f = resize_image(f, _size)
				label = names_with_labels[name]
				labels_with_images[label] += [f]
				cv2.imshow('Adding face to traning set...', f)
				cv2.waitKey(5)
	finally:
		cv2.destroyAllWindows()
		return labels_with_images, names_with_labels


def produce_training_data(path: str, who: str):
	output_dir = os.sep.join([path, who])
	output = os.sep.join([output_dir, who])
	os.mkdir(output_dir)
	timeout = 2000

	try:
		cap = cv2.VideoCapture(0)
		crop = np.zeros((300, 300, 3), np.uint8)
		count = -1

		while cv2.waitKey(timeout) != 10:
			_, frame = cap.read()
			if frame is not None:
				face = detect_face(frame)
				if face is not None:
					crop = face
					count += 1
					cv2.imwrite(filename=output + '.' + str(count) + '.png', img=crop)
			cv2.imshow('Saved', crop)
	finally:
		cap.release()
		cv2.destroyAllWindows()


def train_recognizer(labels_with_images: dict, recognizer, path: str):
	images = []
	labels = []

	for key, value in labels_with_images.items():
		images += value
		labels += [key for _ in range(len(value))]

	recognizer.train(images, np.array(labels))
	recognizer.save(path)


def resize_image(_img: np.ndarray, _size: int):
	return cv2.resize(_img, (_size, _size))


def detect_face(img: np.ndarray):
	face_cascade = cv2.CascadeClassifier('resources/haarcascade_frontalface_default.xml')
	scale_factor = 1.3
	min_neighbors = 5

	grey_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
	faces = face_cascade.detectMultiScale(image=grey_image, scaleFactor=scale_factor, minNeighbors=min_neighbors)

	if len(faces):
		(x, y, w, h) = faces[0]
		return grey_image[y:y + h, x:x + w]
	else:
		return None


def train():
	resources = 'resources'
	training_data = 'training_data'
	who = 'mate_f'
	size = 150

	# 1. Produce data
	#produce_training_data(path, who)

	# 2. Read training data
	labels_with_images, names_with_labels = get_images_and_labels(path, size)

	# 3. Train & Predict
	integration_test(labels_with_images, names_with_labels, size, path)


if __name__ == '__main__':
	train()
	# integration_test()
