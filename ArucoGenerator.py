import sys
import argparse
import numpy as np
import cv2
import cv2.aruco as aruco

DEBUG = False

def createParser():
	parser = argparse.ArgumentParser()

	#size of field
	parser.add_argument('-s',
				'--side',
				'--side_length',
				type = int,
				help = 'Defines side of each marker in millimeters')

	#name of paper
	parser.add_argument('-p',
				'--paper',
				'--paper_name',
				help = 'Defines name of paper to use. A3, A4, USER. If "USER" have chosen,\
				additional parameters --width and --height should be defined')

	#paper width
	parser.add_argument('--width',type = int, help='width of user-sized paper')

	#paper height
	parser.add_argument('--height',type = int,help = 'height of user-sized heiht')

	#image filename
	parser.add_argument('-n', '--filename',help = 'filename of output image')

	#resolution of picture
	parser.add_argument('--ppm',
				'--pixels_per_millimeter',
				type = int,
				help = 'defines number of pixels per millimeter for output picture')

	parser.add_argument('--ignore_gaps',nargs='+', help = 'Defines which gaps near border can be ignored. \
						Example: --ignore_gaps TOP BOTTOM LEFT RIGHT')

	parser.add_argument('--start_id', type = int, help = "Marker's numbers starts whith this id")
	return parser

def createPrintableMap(paper_size,
		marker_size,
		start_id = 0,
		dict = aruco.DICT_4X4_1000,
		ppm = 10,
		gap_coef = 1/3,
		gaps_ignored = []):

	image_resolution = [x*ppm for x in paper_size]

	marker_resolution = marker_size*ppm
	if DEBUG: print("marker resolution = {}".format(marker_resolution))

	gap = int(marker_resolution*gap_coef)
	if DEBUG: print("gap = {}".format(gap))

	mg_resolution = marker_resolution+gap
	if DEBUG: print("mg_resolution = {}".format(mg_resolution))

	aruco_dict = aruco.Dictionary_get(dict)

	# Here we calculating maxium possible columns and rows we can
	# achieve with given size of paper and gap
	if DEBUG: print(mg_resolution)

	if DEBUG: print(image_resolution[0])
	if DEBUG: print(image_resolution[1])
	rows = int(image_resolution[0] / mg_resolution)
	if DEBUG: print("gaps_ignored = {}".format(gaps_ignored))

	top_gap = int(not ('TOP' in gaps_ignored))
	if DEBUG: print("top_gap = {}".format(top_gap))
	bottom_gap = int (not ('BOTTOM' in gaps_ignored))
	if DEBUG: print("bottom_gap = {}".format(bottom_gap))
	supposed_height = (rows*mg_resolution - gap) + top_gap*gap+bottom_gap*gap

	if DEBUG: print("supposed height = {}".format(supposed_height))
	if image_resolution[0] < supposed_height: rows = rows-1


	cols = int(image_resolution[1] / mg_resolution)

	left_gap = int(not 'LEFT' in gaps_ignored)
	if DEBUG: print("left gap = {}".format(left_gap))
	right_gap = int (not 'RIGHT' in gaps_ignored)
	if DEBUG: print("right gap = {}".format(right_gap))

	# |--left_gap--|--(cols*mg_resolution - gap)--|--right_gap--|
	supposed_width = (cols*mg_resolution - gap) + left_gap*gap+right_gap*gap

	if DEBUG: print("supposed width = {}".format(supposed_width))
	if image_resolution[1] < supposed_width: cols = cols-1

	# Up to this point, was a calculation of parameters which is useful for map
	# creation. Now, creating map itself

	actual_image = createMap(rows,cols,marker_resolution,gap,start_id, ppm, aruco_dict)
	image_size = actual_image.shape
	# Here, just created map will aligned due to command line arguments
	#actual_image = result[0:endpoint[0],0:endpoint[1]]

	x = gap*top_gap
	y = gap*left_gap
	result = np.zeros((image_resolution[0],image_resolution[1]),dtype = 'uint8') + 255
	result[x:x+image_size[0],y:y+image_size[1]] = actual_image
	return result

def createMap(rows,cols,marker_resolution,gap,start_id, ppm,aruco_dict):
	# To create a map, we need to know these parameters:
	# pixel p millimeter,rows of map, columns of map, gap and marker resolution
	# and id to start with.
	mg_resolution = marker_resolution+gap
	image_size = [mg_resolution*rows-gap, mg_resolution*cols - gap]
	actual_image = np.zeros((image_size[0],image_size[1]),dtype = 'uint8') + 255

	id = start_id
	#filling image with markers
	for row in range(rows):
		for col in range(cols):
			x = mg_resolution*row
			y = mg_resolution*col
			marker = aruco.drawMarker(aruco_dict, id, marker_resolution)
			actual_image[x:x+marker_resolution,y:y+marker_resolution] = marker
			id = id + 1
	return actual_image


def createMultiPageMap(map_ratio, paper, ):
	pass

#paper constants in millimeters
PAPER_A3 = [297,420]
PAPER_A4 = [210,297]

#parsing arguments
parser = createParser()
namespace = parser.parse_args()

start_id = namespace.start_id if namespace.start_id else 0

paper = namespace.paper
paper_width = namespace.width
paper_height = namespace.height

gaps_ignored = namespace.ignore_gaps if namespace.ignore_gaps else []

ppm = namespace.ppm

side = namespace.side
filename = namespace.filename if namespace.filename else "out.jpg"

paper = {"A4": PAPER_A4,
		 "A3": PAPER_A3,
		 "USER": [paper_height,paper_width]}[paper.upper()]

if DEBUG: print("paper size: {}".format(paper))
result = createPrintableMap(paper,side,gaps_ignored = gaps_ignored, start_id = start_id)

cv2.imwrite(filename, result)
