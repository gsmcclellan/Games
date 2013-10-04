""" Greg McClellan
	Source Code from inventwithpython.com
					 Al Sweigart al@inventwithpython.com
	2013-9-30

"""


import pygame, sys, random
from pygame.locals import *


# Create the constants (go ahead and experiment with diff values)
BOARDWIDTH = 4
BOARDHEIGHT = 4
TILESIZE = 80
WINDOWWIDTH = 640
WINDOWHEIGHT = 480
FPS = 30
BLANK = None

# Colors (R, G, B)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BRIGHTBLUE = (0, 50, 255)
DARKTURQUOISE = (3, 54, 73)
GREEN = (0, 204, 0)

BGCOLOR = DARKTURQUOISE
TILECOLOR = GREEN
TEXTCOLOR = WHITE
BORDERCOLOR = BRIGHTBLUE
BASICFONTSIZE = 20

BUTTONCOLOR = WHITE
BUTTONTEXTCOLOR = BLACK
MESSAGECOLOR = WHITE

XMARGIN = int((WINDOWWIDTH - (TILESIZE * BOARDWIDTH + (BOARDWIDTH - 1))) / 2)
YMARGIN = int((WINDOWHEIGHT - (TILESIZE * BOARDHEIGHT + (BOARDHEIGHT - 1)))/2)

UP = 'up'
DOWN = 'down'
LEFT = 'left'
RIGHT = 'right'


def main():
	global FPSCLOCK, DISPLAYSURF, BASICFONT, RESET_SURF, RESET_RECT, NEW_SURF, \
		   NEW_RECT, SOLVE_SURF, SOLVE_RECT

	pygame.init()
	FPSCLOCK = pygame.time.Clock()
	DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
	pygame.display.set_caption('Slide Puzzle')
	BASICFONT = pygame.font.Font('freesansbold.ttf', BASICFONTSIZE)

	# Store the option buttons and their rectangles in OPTIONS
	RESET_SURF, RESET_RECT = make_text('Reset',
									   TEXTCOLOR,
									   TILECOLOR,
									   WINDOWWIDTH - 120,
									   WINDOWHEIGHT - 90)
	NEW_SURF, NEW_RECT = make_text('New Game',
								   TEXTCOLOR,
								   TILECOLOR,
								   WINDOWWIDTH - 120,
								   WINDOWHEIGHT - 60)
	SOLVE_SURF, SOLVE_RECT = make_text('Solve',
									   TEXTCOLOR,
									   TILECOLOR,
									   WINDOWWIDTH - 120,
									   WINDOWHEIGHT - 30)

	SOLVEDBOARD = get_starting_board() #Same as the board in a start state
	#import pdb; pdb.set_trace()
	main_board, solution_sequence = generate_new_puzzle(80)
	all_moves = [] # List of moves made from the solved configuration


	while True: # Main game loop
		slide_to = None
		message = "Click tile or press arrow keys to slide"
		if main_board == SOLVEDBOARD:
			message = "Solved!"

		draw_board(main_board, message)

		check_for_quit()

		for event in pygame.event.get(): # Event handling loop

			if event.type == MOUSEBUTTONUP:
				spotx, spoty = get_spot_clicked(main_board, 
												event.pos[0],
												event.pos[1])

				if (spotx, spoty) == (None, None):
					# Check if the user clicked on an option buttons
					if RESET_RECT.collidepoint(event.pos):
						# Clicked on reset button
						reset_animation(main_board, all_moves)
						all_moves = []
					elif NEW_RECT.collidepoint(event.pos):
						# Clicked on New Game button
						main_board, solution_sequence = generate_new_puzzle(80)
						all_moves = []
					elif SOLVE_RECT.collidepoint(event.pos):
						# Clicked on Solve button
						reset_animation(main_board, 
										solution_sequence + all_moves)
						all_moves = []

				else:
					# Check if the clicked tile was next to the blank spot
					blankx, blanky = get_blank_position(main_board)
					if spotx == blankx + 1 and spoty == blanky:
						slide_to = LEFT
					elif spotx == blankx -1 and spoty == blanky:
						slide_to = RIGHT
					elif spotx == blankx and spoty == blanky + 1:
						slide_to = UP
					elif spotx == blankx and spoty == blanky - 1:
						slide_to = DOWN

			elif event.type == KEYUP:
				# Check if the user pressed a key to slide a tile
				if event.key in (K_LEFT, K_a) and is_valid_move(main_board, LEFT):
					slide_to = LEFT
				elif event.key in (K_RIGHT, K_d) and is_valid_move(main_board, RIGHT):
					slide_to = RIGHT
				elif event.key in (K_UP, K_w) and is_valid_move(main_board, UP):
					slide_to = UP
				elif event.key in (K_DOWN, K_s) and is_valid_move(main_board, DOWN):
					slide_to = DOWN

		if slide_to:
			# Show slide on screen
			slide_animation(main_board, 
							slide_to, 
							message,
							8)
			make_move(main_board, slide_to)
			draw_board(main_board, message)
			all_moves.append(slide_to) # Record the slide
		pygame.display.update()
		FPSCLOCK.tick(FPS)


def terminate():
	"""Exits Game"""
	pygame.quit()
	sys.exit()


def check_for_quit():
	"""Checks to see if the user has initiated a quit game action"""
	for event in pygame.event.get(QUIT): # Get all the QUIT events
		terminate() # Terminate if any are present

	for event in pygame.event.get(KEYUP): # Gets all KEYUP events
		if event.key == K_ESCAPE:
			terminate() # Terminate if user presses K_ESCAPE
		pygame.event.post(event) # Put the other KEYUP event objects BLACK


def get_starting_board():
	"""Return a solved board"""
	counter = 1
	board = []

	for x in range(BOARDWIDTH):
		column = []

		for y in range(BOARDHEIGHT):
			column.append(counter)
			counter += BOARDWIDTH

		board.append(column)
		counter -= BOARDWIDTH * (BOARDHEIGHT - 1) + BOARDWIDTH - 1

	board[BOARDWIDTH - 1][BOARDHEIGHT - 1] = None
	return board


def get_blank_position(board):
	"""Return the x and y coordinates of the blank space"""
	for x in range(BOARDWIDTH):

		for y in range(BOARDHEIGHT):

			if board[x][y] == None:
				return (x, y)


def make_move(board, move):
	"""Makes desired move after its validity has been checked"""
	blankx, blanky = get_blank_position(board)

	if move == UP:
		board[blankx][blanky], board[blankx][blanky+1] = \
		board[blankx][blanky+1], board[blankx][blanky]
	elif move == DOWN:
		board[blankx][blanky] = board[blankx][blanky-1]
		board[blankx][blanky-1] = None
	elif move == LEFT:
		board[blankx][blanky] = board[blankx+1][blanky]
		board[blankx+1][blanky] = None
	elif move == RIGHT:
		board[blankx][blanky] = board[blankx-1][blanky]
		board[blankx-1][blanky] = None


def is_valid_move(board, move):
	#Checks to see if desired move is valid
	blankx, blanky = get_blank_position(board)

	if move == UP and blanky != len(board[0]) - 1:
		return True
	elif move == DOWN and blanky != 0:
		return True
	elif move == LEFT and blankx != len(board) - 1:
		return True
	elif move == RIGHT and blankx != 0:
		return True
	else:
		return False


def get_random_move(board, last_move = None):
	#Picks a random move while checking for validity"
	# Start with a full list of all four moves
	possible_moves = [UP, DOWN, LEFT, RIGHT]

	# Remove moves from the list as they are disqualified
	if last_move == UP or not is_valid_move(board, DOWN):
		possible_moves.remove(DOWN)
	if last_move == DOWN or not is_valid_move(board, UP):
		possible_moves.remove(UP)
	if last_move == LEFT or not is_valid_move(board, RIGHT):
		possible_moves.remove(RIGHT)
	if last_move == RIGHT or not is_valid_move(board, LEFT):
		possible_moves.remove(LEFT)

	# Return a random move from the list of remaining moves
	return random.choice(possible_moves)


def get_left_top_of_tile(tileX, tileY):
	"""Takes our tile position and returns actual pixel position"""
	left = XMARGIN + (tileX * TILESIZE) + (tileX - 1)
	top = YMARGIN + (tileY * TILESIZE) + (tileY - 1)
	return (left, top)





def get_spot_clicked(board, x, y):
	"""From x&y board coordinates, get the x&y pixel coordinates"""

	for tile_x in range(len(board)):

		for tile_y in range(len(board[0])):
			left, top = get_left_top_of_tile(tile_x, tile_y)
			tile_rect = pygame.Rect(left, top, TILESIZE, TILESIZE)

			if tile_rect.collidepoint(x, y):
				return (tile_x, tile_y)

	return (None, None)


def draw_tile(tile_x, tile_y, number, adjx=0, adjy=0):
	"""Draw a tile at board coordinates tile_x and tile_y, with optional
	adjustment using adjx and adjy"""
	left, top = get_left_top_of_tile(tile_x, tile_y)
	pygame.draw.rect(DISPLAYSURF, 
					 TILECOLOR, 
					 (left + adjx, top + adjy, TILESIZE, TILESIZE))
	text_surf = BASICFONT.render(str(number), True, TEXTCOLOR)
	text_rect = text_surf.get_rect()
	text_rect.center = left + int(TILESIZE / 2) + adjx, \
					   top + int(TILESIZE / 2) + adjy
	DISPLAYSURF.blit(text_surf, text_rect)


def make_text(text, color, bgcolor, top, left):
	"""Create the Surface and Rect Objects for some text"""
	text_surf = BASICFONT.render(text, True, color, bgcolor)
	text_rect = text_surf.get_rect()
	text_rect.topleft = (top, left)
	return (text_surf, text_rect)


def draw_board(board, message):
	DISPLAYSURF.fill(BGCOLOR)
	if message:
		text_surf, text_rect = make_text(message, MESSAGECOLOR, BGCOLOR, 5, 5)
		DISPLAYSURF.blit(text_surf, text_rect)

	for tile_x in range(len(board)):

		for tile_y in range(len(board[0])):

			if board[tile_x][tile_y]:
				draw_tile(tile_x, tile_y, board[tile_x][tile_y])


	left, top = get_left_top_of_tile(0, 0)
	width = BOARDWIDTH * TILESIZE
	height = BOARDHEIGHT * TILESIZE
	pygame.draw.rect(DISPLAYSURF, 
						BORDERCOLOR, 
						(left - 5, top - 5, width + 11, height + 11), 
						4)

	DISPLAYSURF.blit(RESET_SURF, RESET_RECT)
	DISPLAYSURF.blit(NEW_SURF, NEW_RECT)
	DISPLAYSURF.blit(SOLVE_SURF, SOLVE_RECT)



def slide_animation(board, direction, message, animation_speed):
	#creates the animation for each move""
	blankx, blanky = get_blank_position(board)

	if direction == UP:
		movex = blankx
		movey = blanky + 1
	elif direction == DOWN:
		movex = blankx
		movey = blanky - 1
	elif direction == LEFT:
		movex = blankx + 1
		movey = blanky
	elif direction == RIGHT:
		movex = blankx - 1
		movey = blanky

	# Prepare the base Surface
	draw_board(board, message)
	base_surf = DISPLAYSURF.copy()

	# Draw a blank space over the moving tile on the base_surf Surface
	move_left, move_top = get_left_top_of_tile(movex, movey)
	pygame.draw.rect(base_surf, 
					 BGCOLOR, 
					 (move_left, move_top, TILESIZE, TILESIZE))

	for i in range(0, TILESIZE + 1, animation_speed):
		# Animate the tile sliding over
		check_for_quit()
		DISPLAYSURF.blit(base_surf, (0, 0))
		if direction == UP:
			draw_tile(movex, movey, board[movex][movey], 0, -i)
		if direction == DOWN:
			draw_tile(movex, movey, board[movex][movey], 0, i)
		if direction == LEFT:
			draw_tile(movex, movey, board[movex][movey], -i, 0)
		if direction == RIGHT:
			draw_tile(movex, movey, board[movex][movey], i, 0)

		pygame.display.update()
		FPSCLOCK.tick(FPS)



def generate_new_puzzle(num_slides):
	"""Applies a number of random slides equal to num_slides"""
	sequence = []
	starting_board = get_starting_board()
	draw_board(starting_board, "")
	pygame.display.update()
	pygame.time.wait(500) # Pause 500 milliseconds for effect
	last_move = None

	for i in range(num_slides):
		move = get_random_move(starting_board, last_move)
		slide_animation(starting_board, 
						move, 
						'Generating new puzzle...', 
						animation_speed=int(TILESIZE/3))
		make_move(starting_board, move)
		sequence.append(move)
		last_move = move

	return (starting_board, sequence)



def reset_animation(board, all_moves):
	"""Make all of the moves in all_moves in reverse"""
	rev_all_moves = all_moves[:]
	rev_all_moves = rev_all_moves[::-1]

	for move in rev_all_moves:
		if move == UP:
			opposite_move = DOWN
		elif move == DOWN:
			opposite_move = UP
		elif move == LEFT:
			opposite_move = RIGHT
		elif move == RIGHT:
			opposite_move = LEFT

		slide_animation(board, opposite_move, "", int(TILESIZE/2))
		make_move(board, opposite_move)


if __name__ == '__main__':
	main()

