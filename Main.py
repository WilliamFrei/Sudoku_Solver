#!/usr/bin/env python
"""

A Python3 program that, if you run into any mistakes while solving a Sudoku puzzle, identifies those mistakes for you.

This module mainly contains glue code tying together the other modules.

Mistakes happen from time to time when solving Sudoku. Possible reasons are miscounting, switching up rows with other rows (or the same with columns), or simply faulty solving logic, among other things.
When that happens, it is usually only after you fill out several more (potentially wrong, as a consequence of the original mistake) squares that you notice a the mistake has transpired.
At this point, it can be very hard to pinpoint the original mistake. This program tries to help with that, by showing you all the squares that are filled out wrong.


The user first inputs the Sudoku problem (i.e. the numbers originally filled out).
Then they also input their (complete or incomplete) solution (i.e. the numbers added by the them).
The solver first checks if the Sudoku problem has exactly one solution - if this isn't the case then the problem is not a valid Sudoku.
Then it compares the user's solution to the actual solution, and outputs all the squares where the user's solution is wrong.
The user can then erase those numbers and restart their solving effort, hopefully correctly solving the Sudoku this time!


Some additional notes:
This program calculates the actual solution to the Sudoku, but it does not show that solution to the user, so that the user can still solve the puzzle themselves.
However, this program can still be used to brute-force-solve a Sudoku for you, by calling it at most 8 times if done intelligently. But if you just want the solution, then there are hundreds of Sudoku solvers you can find on the internet that will present you the solution immediately.

Implementation details:
The method used internally for solving the Sudoku is a SAT-Solver, which only works with binary variables. Thus, for every square in the Sudoku, there are 9 variables (one for each of the digits used in classic Sudokus), of which exactly one is true.
SAT-Solvers operates on CNFs (Conjunctive Normal Forms), which is a structure that consits of a set of clauses which all have to be true.
A clause is a set of literals (which are either variables or negated variables), and a clause is true if at least one of the literal it contains is true.
An example CNF would be {{-1, -2}, {1, -2}, {1, 2}}, in this case it consists of three clauses. The first clause that is true if either variable is false (the "-" denotes the negation), the 2nd clause is true if the first variable is true or the second variable is false, and the  third clause is true if either variable is true. For this CNF and the two given variables, there is 1 solution variable assignment: {1, -2} (the solution assigns variable 1 to true and variable 2 to false).
A valid Sudoku puzzle has exactly one such solution assignment. The assignment can be uniquely determined by a CNF that encodes the usual Sudoku restrictions (numbers 1-9 appearing exactly once in each row, column and 3x3-subgrid, exactly one number appearing in each square, together with some squares that are already filled with numbers).

"""

import numpy as np

from modules.Solver import Solver
from modules.generate_sudoku_cnf import get_complete_sudoku_clauses, split_global_identifier
from modules.visualisation import draw_sudoku, draw_attempt

def solve_puzzle(puzzle: np.array):
	"""
	Solves the Sudoku puzzle passed as parameter.
	"""
	# asserts are in 'get_complete_sudoku_clauses'
	clauses = get_complete_sudoku_clauses(puzzle)
	solver = Solver(clauses, 9 ** 3)
	solved = solver.solve()
	assert solved
	solution_vars = solver.get_solution()
	solution_arr = np.empty((9,9), dtype=int)
	for var in solution_vars:
		x, y, i = split_global_identifier(var)
		solution_arr[y, x] = i
		if puzzle[y, x] > 0:
			assert puzzle[y, x] == i # assert the solution does not clash with the original puzzle
	
	return solution_arr


def solve_and_compare(puzzle: np.array, filled: np.array=None):
	"""
	Solves the Sudoku puzzle and optionally compares it to a (possibly partially) filled out Sudoku.
	If such a filled out Sudoku was passed as an argument, the differences in solutions is shown (empty fields ommitted).
	If no such filled out Sudoku was passed as an argument, the whole solution to the puzzle is shown.
	"""
	# only check 'filled' as 'puzzle' is checked in a sub-call of 'solve_puzzle'
	assert filled is None or filled.shape == (9, 9), f"'filled' array has wrong shape in 'solve_and_compare' call, should be (9, 9) but is: {filled.shape}"
	assert filled is None or (0 <= np.min(filled) and np.max(filled) <= 9), f"'filled' array entries out of bounds (>= 9 or <= 0) in 'array_to_clauses' call: {filled}"
	
	solution_arr = solve_puzzle(puzzle)
			
	'''
	# to use the steps in 'draw_progress', we need them as (i, x, y, n) tuples, so they need to be converted with 'split_global_identifier' first
	step_tuples = [(iteration, *split_global_identifier(step)) for iteration, step in solver.get_steps()]
	draw_progress(step_tuples)
	'''
	
	if filled is None:
		draw_sudoku(solution_arr)
	else:
		squares = np.nonzero(filled)
		#diff_arr = np.zeros((9,9), dtype=int)
		#diff_arr[squares] = filled[squares] * (filled[squares] != solution_arr[squares])
		draw_attempt(puzzle, filled, solution_arr)


if __name__ == '__main__':
	# code below is for testing functionality
	
	from modules.sudoku_examples import sdk_givens, sdk_filled
	
	solve_and_compare(sdk_givens[0], sdk_filled[0])
	solve_and_compare(sdk_givens[1], sdk_filled[1])
	solve_and_compare(sdk_givens[2], sdk_filled[2])
	
	#solve_and_compare(sdk_givens[0])
	
	
	#draw_sudoku(sdk_givens[0])
	
	#draw_attempt(sdk_givens[0], sdk_filled[0])
	
	#draw_attempt(sdk_givens[0], sdk_givens[0])
	


