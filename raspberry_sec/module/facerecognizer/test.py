import cv2
import os
import sys
import numpy as np
import json
import logging
sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))
from raspberry_sec.module.facedetector.consumer import FacedetectorConsumer
from raspberry_sec.module.facerecognizer.consumer import FacerecognizerConsumer
from raspberry_sec.interface.consumer import ConsumerContext


logging.basicConfig(format='%(asctime)s:%(name)s:%(levelname)s - %(message)s', level=logging.DEBUG)


def set_parameters():
	parameters = dict()
	parameters['eigen_components'] = 7
	parameters['eigen_enabled'] = True
	parameters['eigen_model'] = 'resources/eigen.yml'
	parameters['eigen_threshold'] = 2000.0
	parameters['fisher_components'] = 7
	parameters['fisher_enabled'] = True
	parameters['fisher_model'] = 'resources/fisher.yml'
	parameters['fisher_threshold'] = 500.0
	parameters['label_map'] = 'resources/labels.json'
	parameters['lbph_enabled'] = True
	parameters['lbph_height'] = 7
	parameters['lbph_model'] = 'resources/lbph.yml'
	parameters['lbph_neighbors'] = 8
	parameters['lbph_radius'] = 5
	parameters['lbph_threshold'] = 80.0
	parameters['lbph_width'] = 7
	parameters['size'] = 100
	return parameters


def set_detector_parameters():
	parameters = dict()
	parameters['cascade_file'] = 'resources/haarcascade_frontalface_default.xml'
	parameters['min_neighbors'] = 5
	parameters['scale_factor'] = 1.3
	parameters['timeout'] = 1
	return parameters


def integration_test():
	# Given
	detector_consumer = FacedetectorConsumer(set_detector_parameters())
	recognizer_consumer = FacerecognizerConsumer(set_parameters())
	context = ConsumerContext(None, False)
	cap = cv2.VideoCapture(0)

	# When
	try:
		while cv2.waitKey(50) == -1:
			success, frame = cap.read()
			# Detection
			if success:
				context.data = frame
				detector_consumer.run(context)
				face = context.data
			# Recognition
			if context.alert:
				recognizer_consumer.run(context)
				face = resize_image(face, 300)
				cv2.putText(face, context.alert_data, (5, 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
				cv2.imshow('Face', face)
	finally:
		cap.release()
		cv2.destroyAllWindows()


def train():
	parameters = set_parameters()
	labels_with_images, names_with_labels = get_images_and_labels('training_data', parameters['size'])

	# Eigen
	path = parameters['eigen_model']
	recognizer = cv2.face.EigenFaceRecognizer_create(
		num_components=parameters['eigen_components'],
		threshold=parameters['eigen_threshold']
	)
	train_recognizer(labels_with_images, recognizer, path)

	# Fisher
	path = parameters['fisher_model']
	recognizer = cv2.face.FisherFaceRecognizer_create(
		num_components=parameters['fisher_components'],
		threshold=parameters['fisher_threshold']
	)
	train_recognizer(labels_with_images, recognizer, path)

	# LBPH
	path = parameters['lbph_model']
	recognizer = cv2.face.LBPHFaceRecognizer_create(
		radius=parameters['lbph_radius'],
		neighbors=parameters['lbph_neighbors'],
		grid_x=parameters['lbph_width'],
		grid_y=parameters['lbph_height'],
		threshold=parameters['lbph_threshold']
	)
	train_recognizer(labels_with_images, recognizer, path)

	# Label mapping (name to label)
	with open(parameters['label_map'], 'w+') as labelmap:
		json.dump(fp=labelmap, obj=names_with_labels, indent=4, sort_keys=True)


def train_recognizer(labels_with_images: dict, recognizer, path: str):
	images = []
	labels = []

	for key, value in labels_with_images.items():
		images += value
		labels += [key for _ in range(len(value))]

	recognizer.train(images, np.array(labels))
	recognizer.write(path)


def get_images_and_labels(path: str, size: int):
	labels_with_images = {}
	names_with_labels = {}
	image_paths = []
	detector_consumer = FacedetectorConsumer(set_detector_parameters())
	context = ConsumerContext(None, False)

	for root, dirs, files in os.walk(path):
		image_paths += [os.sep.join([root, file]) for file in files if file.endswith('.png')]

	global_label = 0
	try:
		for image_path in image_paths:
			image = cv2.imread(image_path)

			# Detect face in image
			context.data = image
			detector_consumer.run(context)
			face = context.data

			if face is not None and context.alert:
				name = os.path.split(image_path)[1].split('.')[0]
				if not names_with_labels.__contains__(name):
					names_with_labels[name] = global_label
					labels_with_images[global_label] = []
					global_label += 1

				face = resize_image(face, size)
				label = names_with_labels[name]
				labels_with_images[label].append(face)
				cv2.imshow('Adding face to traning set...', face)
				cv2.waitKey(5)
	finally:
		cv2.destroyAllWindows()
		return labels_with_images, names_with_labels


def resize_image(_img: np.ndarray, _size: int):
	return cv2.resize(_img, (_size, _size))


def produce_training_data(who: str, timeout: int=2000):
	output_dir = os.sep.join(['training_data', who])
	output = os.sep.join([output_dir, who])
	os.mkdir(output_dir)

	context = ConsumerContext(None, False)
	detector_consumer = FacedetectorConsumer(set_detector_parameters())
	cap = cv2.VideoCapture(0)

	try:
		count = -1
		while cv2.waitKey(timeout) == -1:
			success, frame = cap.read()
			if success:
				context.data = frame
				detector_consumer.run(context)
				face = context.data
			if context.alert:
				count += 1
				cv2.imwrite(filename=output + '.' + str(count) + '.png', img=face)
				cv2.imshow('Saved', face)
	finally:
		cap.release()
		cv2.destroyAllWindows()


if __name__ == '__main__':
	# produce_training_data('mate_c', 500)
	train()
	integration_test()
