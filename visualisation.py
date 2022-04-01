"""
Functions to visualize Sudokus and/or solving progress
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

from matplotlib.animation import FuncAnimation
from collections.abc import Iterable


def draw_grid():
	"""
	Helper function to draw a normal Sudoku grid.
	"""
	fig = plt.figure(figsize=(10, 10), frameon=False)
	
	plt.axis('off')
	
	# the sudoku grid, consisting of 10 vertical and 10 horizontal lines
	for c in range(10):
		plt.plot((c, c), (0, 9), zorder=6, color='black', linewidth=4 if c % 3 == 0 else 1)
		plt.plot((0, 9), (c, c), zorder=6, color='black', linewidth=4 if c % 3 == 0 else 2)
	
	return fig

def draw_grid_plus(sudoku: np.array):
	"""
	Helper function that draws a Sudoku grid and fills it with the nonzero entries in 'sudoku'.
	"""
	assert False, "Not implemented yet"

def draw_sudoku(sudoku: np.array):
	"""
	Takes a 9x9 numpy array and visualizes it.
	
	The array may only contain integers from 0 to 9, 0s are interpreted as unfilled squares and left empty in the graphical representation.
	
	sudoku: the 9x9 numpy array to be visualized
	"""
	assert sudoku.shape == (9, 9)
	assert 0 <= np.min(sudoku) and np.max(sudoku) <= 9
	
	draw_grid()
	
	# show the numbers
	for x in range(9):
		for y in range(9):
			c = sudoku[x,y]
			# 0 = empty
			if c > 0:
				plt.text(x + 0.38, y + 0.3, str(c), zorder=4, size=25.0)
	
	plt.show()


def draw_progress(steps: Iterable):
	"""
	Takes a sequence of Sudoku entries visualizes it.
	
	The array may only contain integers from 0 to 9, 0s are interpreted as unfilled squares and left empty in the graphical representation.
	
	steps: the sequence to be visualized, each entry is a 3-tuple of the form (x, y, n) where x and y determine a Sudoku cell and n determines the number in that cell
	"""
	
	# basic asserts for 'steps'
	prev_iteration = 0
	n_givens = 0 # also keep track of how many 'givens' there are
	for iteration, x, y, n in steps:
		assert 0 <= x <= 8
		assert 0 <= y <= 8
		assert 1 <= n <= 9
		
		assert iteration >= prev_iteration
		prev_iteration = iteration
		# if 'iteration' is 0, then the number is a 'given' and not derived
		if iteration == 0:
			n_givens += 1
	
	fig = draw_grid()
	ax = fig.gca()
	
	# separate the steps into givens and actual solution steps
	givens = steps[:n_givens]
	steps = steps[n_givens:]
	# enter the givens into the grid
	for iteration, x, y, n in givens:
		assert iteration == 0
		plt.text(x + 0.38, y + 0.3, str(n), zorder=4, size=25.0)
	
	def draw_step(idx):
		
		print('~', idx)
		ax = fig.gca()
		# clear the patch we added in the previous 'draw_step' call (if any)
		ax.patches.clear()
		# if we are at the beginning (idx < 0), we skip drawing numbers so that the gif shows the inital givens for several frames
		# additionally, if the index is equal to the number of steps, then we are finished
		if idx < 0 or idx == len(steps):
			return fig
		
		# get the value of the previous iteration, or 0 if this is the first real step
		if idx == 0:
			prev_iteration = 0
		else:
			prev_iteration, _, _, _ = steps[idx - 1]
		
		# show the numbers
		iteration, x, y, n = steps[idx]
		assert iteration > 0
		# write the number in the corresponding Sudoku square
		text = plt.text(x + 0.38, y + 0.3, str(n), zorder=4, size=25.0)
		
		# highlight the Sudoku square so that the user can quickly identify which one was changed
		# if there were one or more guesses, then the difference in 'iterations' is 100 or more and the square is colored differently
		rect = mpatches.Rectangle((x, y), 1, 1, fill = True, color = 'lightgreen' if iteration - prev_iteration < 100 else "yellow", linewidth = 0, zorder=2)
		ax.add_patch(rect)
		
		return text,
	
	# the steps before 0 ('range(-3,...)') are frames where nothing changes
	# the +1 step in the 'range' is used to clear the background from the square filled last
	anim = FuncAnimation(fig, draw_step, frames=range(-3, len(steps) + 1), interval=200, repeat=False)
	
	plt.show()


def draw_differences(solved, attempted):
	"""
	Visualizes the user-filled Sudoku, highlighting mistakes.
	"""
	fig = draw_grid()
	ax = fig.gca()
	
	for x in range(9):
		for y in range(9):
			n = attempted[x, y]
			# zeros are treated as unfilled squares and skipped
			if n == 0:
				continue
			# color the background of the square red if the number is wrong
			if solved[x, y] != n:
				rect = mpatches.Rectangle((x, y), 1, 1, fill = True, color = 'tomato', linewidth = 0, zorder=2)
				ax.add_patch(rect)
			# show the number entered by the user
			text = plt.text(x + 0.38, y + 0.3, str(n), zorder=4, size=25.0)
	
	plt.show()


