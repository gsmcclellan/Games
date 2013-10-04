""" Memory Puzzle
	Greg McClellan
	Source Code from: http://inventwithpython.com/pygame
					  Al Sweigart al@inventwithpython.com
	2013-9-30
"""

import random, pygame, sys
from pygame.locals import *

FPS = 30
WINDOWWIDTH = 640
WINDOWHEIGHT = 480
REVEALSPEED = 8 # speed boxes' sliding reveals and covers
BOXSIZE = 60
GAPSIZE = 10
BOARDWIDTH = 8
BOARDHEIGHT = 5
assert (BOARDWIDTH*BOARDHEIGHT)%2 == 0, \
		'Board needs to have an even number of boxes for match pairs'
XMARGIN = int((WINDOWWIDTH - (BOARDWIDTH * (BOXSIZE + GAPSIZE)))/2)
YMARGIN = int((WINDOWHEIGHT - (BOARDHEIGHT * (BOXSIZE + GAPSIZE)))/2)

# RGB colors
GRAY = (100, 100, 100)
NAVYBLUE = (60, 60, 60)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 128, 0)
PURPLE = (255, 0, 255)
CYAN = (0, 255, 255)

BGCOLOR = NAVYBLUE
LIGHTBGCOLOR = GRAY
BOXCOLOR = WHITE
HIGHLIGHTCOLOR = BLUE

DONUT = 'donut'
SQUARE = 'square'
DIAMOND = 'diamond'
LINES = 'lines'
OVAL = 'oval'

ALLCOLORS = (RED, GREEN, BLUE, YELLOW, ORANGE, PURPLE, CYAN)
ALLSHAPES = (DONUT, SQUARE, DIAMOND, LINES, OVAL)
assert len(ALLCOLORS) * len(ALLSHAPES) * 2 >= BOARDWIDTH * BOARDHEIGHT, \
		"Board is too big for the number of shapes/colors defined."


def main():
	global FPSCLOCK, DISPLAYSURFACE
	pygame.init()
	FPSCLOCK = pygame.time.Clock()
	DISPLAYSURFACE = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))

	mousex = 0 # used to store x coord of mouse event
	mousey = 0 # used to store y coord of mouse event
	pygame.display.set_caption('Memory Game')

	main_board = get_randomized_board()
	revealed_boxes = generate_revealed_boxes_data(False)

	first_selection = None # stores the (x, y) of the first box clicked.

	DISPLAYSURFACE.fill(BGCOLOR)
	start_game_animation(main_board)

	while True: # Main game loop
		mouse_clicked = False

		DISPLAYSURFACE.fill(BGCOLOR) # Drawing the window
		draw_board(main_board, revealed_boxes)

		for event in pygame.event.get(): # Event handling loop
			if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
				pygame.quit()
				sys.exit()

			elif event.type == MOUSEMOTION:
				mousex, mousey = event.pos

			elif event.type == MOUSEBUTTONUP:
				mousex, mousey = event.pos
				mouse_clicked = True

		boxx, boxy = get_box_art_pixel(mousex, mousey)

		if boxx != None and boxy != None:
			# The mouse is currently over a box.

			if not revealed_boxes[boxx][boxy]:
				draw_highlight_box(boxx, boxy)

			if not revealed_boxes[boxx][boxy] and mouse_clicked:
				reveal_boxes_animation(main_board, [(boxx, boxy)])
				revealed_boxes[boxx][boxy] = True #Set the box as 'revealed'

				if first_selection == None: # Current box is first one clicked
					first_selection = (boxx, boxy)
				else:
					# Check if there is a match between two icons
					icon1shape, icon1color = get_shape_and_color(
							main_board, 
							first_selection[0], 
							first_selection[1])
					icon2shape, icon2color = get_shape_and_color(
							main_board, 
							boxx, 
							boxy)

					if icon1shape != icon2shape or icon1color != icon2color:
						# Icons don't match. Re-cover up both selections.
						pygame.time.wait(1000) #1000 miliseconds = 1 sec
						cover_boxes_animation(
								main_board, 
								[(first_selection[0], first_selection[1]),
								(boxx, boxy)])
						revealed_boxes[first_selection[0]][first_selection[1]] == False
						revealed_boxes[boxx][boxy] = False
						revealed_boxes[first_selection[0]][first_selection[1]] = False

					elif has_won(revealed_boxes): # Check if all pairs found
						game_won_animation(main_board)
						pygame.time.wait(2000)

						# Reset the Board
						main_board = get_randomized_board()
						revealed_boxes = generate_revealed_boxes_data(False)

						# Show the fully unrevealed board for a second.
						draw_board(main_board, revealed_boxes)
						pygame.display.update()
						pygame.time.wait(1000)

						# Replay the start game animation.
						start_game_animation(main_board)
					first_selection = None

		# Redraw the screen and wait a clock tick
		pygame.display.update()
		FPSCLOCK.tick(FPS)


def generate_revealed_boxes_data(val):

	revealed_boxes = []
	for i in range(BOARDWIDTH):
		revealed_boxes.append([val]*BOARDHEIGHT)
	return revealed_boxes


def get_randomized_board():
	"""Get a list of every possible shape in every possible color"""
	icons = []

	for color in ALLCOLORS:

		for shape in ALLSHAPES:
				icons.append((shape, color))

	random.shuffle(icons) # Randomize the order of the icons list
	num_icons_used = int(BOARDWIDTH * BOARDHEIGHT / 2)
	icons = icons[:num_icons_used]*2 # Make two of each
	random.shuffle(icons)

	# Create the board data structure with randomly placed icons
	board = []

	for x in range(BOARDWIDTH):
		column = []

		for y in range(BOARDHEIGHT):
			column.append(icons[0])
			del icons[0] # Remove icons as we assign them

		board.append(column)

	return board


def split_into_groups_of(groupsize, thelist):
	"""Splits a list into a list of lists, where the inner lists have
	at most groupsize number of items."""
	result = []

	for i in range(0, len(thelist), groupsize):
		result.append(thelist[i:i+groupsize])

	return result


def left_top_coords_of_box(boxx, boxy):
	"""Convert board coordinates to pixel coordinates"""
	left = boxx * (BOXSIZE + GAPSIZE) + XMARGIN
	top = boxy * (BOXSIZE + GAPSIZE) + YMARGIN
	return (left, top)


def get_box_art_pixel(x, y):

	for boxx in range(BOARDWIDTH):

		for boxy in range(BOARDHEIGHT):
			left, top = left_top_coords_of_box(boxx, boxy)
			box_rect = pygame.Rect(left, top, BOXSIZE, BOXSIZE)

			if box_rect.collidepoint(x, y):
				return (boxx, boxy)

	return (None, None)


def draw_icon(shape, color, boxx, boxy):
	quarter = int(BOXSIZE * .25)
	half = int(BOXSIZE * .5)

	left, top = left_top_coords_of_box(boxx, boxy) # get pixel coords from board coords
	#Draw the shapes
	if shape == DONUT:
		pygame.draw.circle(DISPLAYSURFACE, color, (left+half, top+half), half-5)
		pygame.draw.circle(DISPLAYSURFACE, BGCOLOR, (left+half, top+half), quarter-5)

	elif shape == SQUARE:
		pygame.draw.rect(DISPLAYSURFACE, 
						 color, 
						 (left+quarter, 
							 top+quarter, 
							 BOXSIZE-half, 
							 BOXSIZE-half))

	elif shape == DIAMOND:
		pygame.draw.polygon(DISPLAYSURFACE, 
							color, 
							((left+half, top), 
								(left+BOXSIZE-1, top+half), 
								(left+half, top+BOXSIZE-1), 
								(left, top+half)))

	elif shape == LINES:

		for i in range(0, BOXSIZE, 4):
			pygame.draw.line(DISPLAYSURFACE, 
							 color, 
							 (left, top+i), 
							 	(left+i, top))
			pygame.draw.line(DISPLAYSURFACE, 
							 color, 
							 (left+i, top+BOXSIZE-1), 
							 	(left+BOXSIZE-1, top+i))

	elif shape == OVAL:
		pygame.draw.ellipse(DISPLAYSURFACE, 
							color, 
							(left, top+quarter, BOXSIZE, half))


def get_shape_and_color(board, boxx, boxy):
	"""Shape and color value for a given box"""
	# Shape value for x, y spot is stored in board[x][y][0]
	# Color value for x, y spot is stored in board[x][y][1]
	return board[boxx][boxy][0], board[boxx][boxy][1]


def draw_box_covers(board, boxes, coverage):
	"""Draws boxes being covered/revealed"""
	for box in boxes:
		left, top = left_top_coords_of_box(box[0], box[1])
		pygame.draw.rect(DISPLAYSURFACE, BGCOLOR, (left, top, BOXSIZE, BOXSIZE))
		shape, color = get_shape_and_color(board, box[0], box[1])
		draw_icon(shape, color, box[0], box[1])

		if coverage > 0: # only draw the cover if there is a coverage
			pygame.draw.rect(DISPLAYSURFACE, 
							 BOXCOLOR, 
							 (left, top, coverage, BOXSIZE))

	pygame.display.update()
	FPSCLOCK.tick(FPS)


def reveal_boxes_animation(board, boxes_to_reveal):
	"""Do the 'box reveal' animation"""
	for coverage in range(BOXSIZE, (-REVEALSPEED)-1, -REVEALSPEED):
		draw_box_covers(board, boxes_to_reveal, coverage)


def cover_boxes_animation(board, boxes_to_cover):
	"""Do the 'box cover' animation"""
	for coverage in range(0, BOXSIZE + REVEALSPEED, REVEALSPEED):
		draw_box_covers(board, boxes_to_cover, coverage)


def draw_board(board, revealed):
	""" Draws all of the boxes in their covered or revealed state"""
	for boxx in range(BOARDWIDTH):

		for boxy in range(BOARDHEIGHT):
			left, top = left_top_coords_of_box(boxx, boxy)

			if not revealed[boxx][boxy]:
				# Draw a covered boxes_to_reveal
				pygame.draw.rect(DISPLAYSURFACE, BOXCOLOR, (left, top, BOXSIZE, BOXSIZE))

			else:
				# Draw the revealed icon
				shape, color = get_shape_and_color(board, boxx, boxy)
				draw_icon(shape, color, boxx, boxy)


def draw_highlight_box(boxx, boxy):
	left, top = left_top_coords_of_box(boxx, boxy)
	pygame.draw.rect(DISPLAYSURFACE, 
					 HIGHLIGHTCOLOR, 
					 (left-5, top-5, BOXSIZE+10, BOXSIZE+10), 
					 4)


def start_game_animation(board):
	# Randomly reveal the boxes 8 at a time.
	covered_boxes = generate_revealed_boxes_data(False)
	boxes=[]

	for x in range(BOARDWIDTH):

		for y in range(BOARDHEIGHT):
			boxes.append((x, y))

	random.shuffle(boxes)
	box_groups = split_into_groups_of(8, boxes)

	draw_board(board, covered_boxes)
	for box_group in box_groups:
		reveal_boxes_animation(board, box_group)
		cover_boxes_animation(board, box_group)


def game_won_animation(board):
	"""Flash the background color when the player has won"""
	covered_boxes = generate_revealed_boxes_data(True)
	color1 = LIGHTBGCOLOR
	color2 = BGCOLOR

	for i in range(13):
		color1, color2 = color2, color1 #Swap colors
		DISPLAYSURFACE.fill(color1)
		draw_board(board, covered_boxes)
		pygame.display.update()
		pygame.time.wait(300)


def has_won(revealed_boxes):
	"""Returns True if all boxes have been revealed, otherwise False"""
	for i in revealed_boxes:
		if False in i:
			return False

	return True


if __name__ == '__main__':
	main()