"""
Functions to visualize sudokus and/or solving progress
"""

import numpy as np
import matplotlib.pyplot as plt

def plot_sudoku(sudoku):
	"""
	Takes a 9x9 numpy array and visualizes it.
	
	The array may only contain integers from 0 to 9, 0s are interpreted as unfilled squares and left empty in the graphical representation.
	
	sudoku: the 9x9 numpy array to be visualized
	"""
	assert sudoku.shape == (9, 9)
	assert 0 <= np.min(sudoku) and np.max(sudoku) <= 9
	
	plt.figure(figsize=(10, 10))
	
	# show the numbers
	for x in range(9):
		for y in range(9):
			c = sudoku[x,y]
			# 0 = empty
			if c > 0:
				plt.text(x + 0.4, y + 0.3, str(c), size=25.0)
	
	# the sudoku grid, consisting of 10 vertical and 10 horizontal lines
	for c in range(10):
		plt.plot((c, c), (0, 9), color='black', linewidth=4 if c % 3 == 0 else 1)
		plt.plot((0, 9), (c, c), color='black', linewidth=4 if c % 3 == 0 else 2)
	
	plt.show()

def plot_progress(steps):
	assert False, "Not implemented yet"


def plot_differences():
	assert False, "Not implemented yet"



# code below is for testing only
from sudoku_examples import sdk_puzzles
plot_sudoku(sdk_puzzles[0])
