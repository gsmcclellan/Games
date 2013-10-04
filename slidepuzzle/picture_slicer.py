""" Picture Slicer
	Greg McClellan
	2013-10-1

	Program will take a picture and slice it into equal squares for use
	in slide puzzle game
"""
from PIL import Image
import os, sys

dirpath = os.path.abspath(os.path.dirname(__file__))

default_address = 'sample_pic.jpg'

rows = 4
cols = 4
size = (400, 400)


def get_picture(address):
	"""Uploads picture of user's choice"""
	picture = Image.open(address)
	return picture


def resize_picture(picture, size):
	"""Resizes picture to appropriate size"""
	if picture.size[0] < picture.size[1]:
		width = size[0]
		#import pdb; pdb.set_trace()
		height = int((float(picture.size[1])/picture.size[0]) * size[0])
	elif picture.size[1] < picture.size[0]:
		height = size[1]
		width = int((float(picture.size[0])/picture.size[1]) * size[1])
	else:
		width = size[0]
		height = size[1]

	picture = picture.resize((width, height))
	return picture



def crop_picture(picture, size):
	"""Crops image to a specifically sized square"""
	assert picture.size[0] >= size[0] and picture.size[1] >= size[1], \
			"Picture is too small"

	crop_box = (((picture.size[0] - size[0])/2),
			((picture.size[1] - size[1])/2),
			((picture.size[0] - size[0])/2) + size[0],
			((picture.size[1] - size[1])/2) + size[1])

	picture = picture.crop(crop_box)

	return picture


def save_picture(picture, address=None):
	"""Gets a save address and saves the image"""
	if not address:
		# Ask for an address
		print "No address"

	picture.save(address)


def main(image_address=default_address, image_save_address=None):
	if len(sys.argv) > 1:
		image_address = sys.argv[1]

	if len(sys.argv) > 2:
		image_save_address = sys.argv[2]
	else:
		if not image_save_address:
			image_save_address = image_address.split('.')
			image_save_address[-2] += '-new'
			image_save_address = '.'.join(image_save_address)
	

	picture = get_picture(image_address)
	picture = resize_picture(picture, size)
	picture = crop_picture(picture, size)
	save_picture(picture, image_save_address)


	address = image_save_address.split('/')
	address[-1] = '/' + address[-1].split('.')[0] + '-album'
	address = dirpath + '/'.join(address)

	pictures = slice_picture(picture, rows, cols)
	save_sliced_picture(pictures, rows, cols, address) 


def slice_picture(picture, rows, cols, size=size):
	"""Splits picture into a given number of rows and columns"""

	pictures = []

	for col in range(cols):

		for row in range(rows):
			box = ((size[0]/cols)*row,
				   (size[1]/rows)*col,
				   ((size[0]/cols)*row) + (size[0]/cols),
				   ((size[1]/rows)*col) + (size[1]/rows))
			pictures.append(picture.crop(box))

	return pictures


def save_sliced_picture(pictures, rows, cols, address=None):
	"""Saves split picture in an album"""
	if not address:
		# Ask for address
		print "No address"

	if not os.path.exists(address):
		os.makedirs(address)

	for img in range(rows * cols):
		imadd = address + '/' + str(img+1)
		#import pdb; pdb.set_trace()
		pictures[img].save(imadd + '.jpg')


if __name__ == '__main__':
	main()