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
from collections.abc import Iterable

from Solver import Solver

from visualisation import draw_sudoku, draw_attempt

def get_global_identifier(x: int, y: int, n: int):
	"""
	Converts a coordinate and a local variable identifier to a global variable identifier, as there are 9 ** 3 = 729 possible indices. Due to 0 being unusable, the output ranges from 1 to 729.
	
	x: the index on the x-axis, ranges from 0 to 8. The leftmost column has the lowest index.
	y: the index on the y-axis, ranges from 0 to 8. The topmost row has the lowest index.
	n: the local variable identifier, ranges from 1 to 9.
	
	Local variable identifiers are only unique within a single square (and thus need additional information to identify that square) while global variable identifiers already include the square.
	E.g. the global variable identifier generated with the call (0, 1, 9) points at a variable which determines whether in the square in the 1st column, 2nd row a '9' is present. As these are boolean 		variables, there is a separate variable for each number from 1 to 9, for each square in the Sudoku. For each square, exactly one of these variables is set to 'True' in the solved Sudoku.
	"""
	
	# basic sanity checks
	assert 0 <= x <= 8, f"x coordinate out of range [0,8] in 'get_global_identifier' call: {x}"
	assert 0 <= y <= 8, f"y coordinate out of range [0,8] in 'get_global_identifier' call: {y}"
	
	assert 1 <= n <= 9, f"variable identifier n out of range [1,9] in 'get_global_identifier' call: {n}"
	
	# calculate the result
	identifier= y * 9 ** 2 + x * 9 + n
	
	# another sanity check
	assert 1 <= identifier <= 729
	
	return identifier


def split_global_identifier(identifier: int):
	"""
	The inverse operation to the function 'get_global_identifier'.
	
	It converts a global identifier back into a (x, y, n) triplet.
	"""
	
	assert 1 <= identifier <= 729, f"global identifier out of range [1, 729] in 'split_global_identifier' call: {identifier}"
	
	# due to the fact that n is not zero-based, 'identifier' has to be reduced by 1 before converting it back
	identifier -= 1
	
	n = (identifier % 9) + 1 # the 1 from above is added back, so that n is still in the range [1, 9] instead of [0, 8]
	x = (identifier // 9) % 9
	y = identifier // 9 ** 2
	
	assert 1 <= n <= 9
	assert 0 <= x <= 8
	assert 0 <= y <= 8
	
	return x, y, n


def test_global_identifier():
	"""
	Tests the above functions for producing valid outputs given valid inputs.
	
	Each global identifier in the range from 1 to 729 should be generated exactly once.
	Additionally it tests whether 'get_global_identifier' and 'split_global_identifier' behave as inverse functions given valid inputs.
	"""
	
	# the sets holding the generated numbers
	identifier_map = {}
	
	# generate global identifiers and check for duplicates
	for x in range(9):
		for y in range(9):
			for n in range(1, 10):
				identifier = get_global_identifier(x, y, n)
				assert identifier not in identifier_map, f"same global identifier generated twice: {identifier_map[identifier]} and ({x}, {y}, {n})"
				identifier_map[identifier] = (x, y, n)
				# tests inversiveness
				assert (x, y, n) == split_global_identifier(get_global_identifier(x, y, n)), f"'get_global_identifier' and 'split_global_identifier' did not work as inverses: {(x, y, n)}"
	
	# check that each appears at least once
	for identifier in range(1, 729 + 1):
		assert identifier in identifier_map, f"global identifier {identifier} not generated"
		# tests inversiveness
		assert identifier == get_global_identifier(*split_global_identifier(identifier)), f"functions 'get_global_identifier' and 'split_global_identifier' did not work as inverses for {identifier}"



def generate_at_most_one(x: int,y: int):
	"""
	Generates a set of clauses that encode that only a single number may appear in the square at (x,y).
	
	x,y: the coordinates of the square
	
	This is done by generating negated variables pair clauses {-i1, -i2} for all variables pairs (i1, i2) in the given coordinates.
	These clauses make sure that out of any 2 variables for a square, at most one can be true. The one true variable determines which number is in the square.
	"""
	assert 0 <= x <= 8 and 0 <= y <= 8, f"x or y out of range [0,8] in 'generate_at_most_one' call: x={x}, y={y}"
	
	# the returned set
	clauses = set()
	
	# these two loops could be optimized in several ways, but are left as-is for the sake of readability
	# e.g. the first range could instead be 'range(1, 9)', as i1=9 will make the second range empty
	for i1 in range(1, 10):
		# as clauses are sets, {-i1, -i2} is the same as {-i2, -i1}, thus it is fine if we only consider the cases where i2 > i1
		for i2 in range(i1 + 1, 10):
			clauses.add(frozenset((-get_global_identifier(x, y, i1), -get_global_identifier(x, y, i2))))
	
	assert len(clauses) == 9 * 8 // 2 # basic sanity check - there are 9 * 8 pairs (i1, i2), if we disregard the order then that number is halfed
	
	return clauses


def generate_at_least_one(grouped_squares: Iterable):
	"""
	Generates a set of clauses that encode that each number from 1 to 9 has to appear exactly once in the given 9 coordinates.
	
	This is used to encode the condition that each number appears exactly once in each row/column/3x3 subgrid.
	
	grouped_squares: a collection of exactly 9 (x,y) pairs - either a row, a column or a 3x3 subgrid
	"""
	
	# sanity checks
	assert len(grouped_squares) == 9, f"grouped_squares contains invalid number of coordinates in 'generate_exactly_once' call: {len(coordinates)}"
	assert len(set(grouped_squares)) == 9, f"grouped_squares contains duplicate coordinates in 'generate_exactly_once' call"
	
	for x,y in grouped_squares:
		assert 0 <= x <= 8, f"x coordinate out of range [0,8] in 'generate_exactly_once' call: {x}"
		assert 0 <= y <= 8, f"y coordinate out of range [0,8] in 'generate_exactly_once' call: {y}"
	
	# the set of clauses that the function will return
	clauses = set()
	
	for i in range(1, 10):
		# i_clause is a clause that encodes that variable i must appear at least once among the coordinates
		i_clause = frozenset({get_global_identifier(x,y,i) for (x,y) in grouped_squares})
		assert len(i_clause) == 9 # very basic sanity check
		clauses.add(i_clause)
		
		# additional clauses that encode that if one square among the 'grouped_squares' contains a number (variable), then no other square among the group may contain the same number
		# this information is redundant due to the fact that only one variable may contain a square and all 9 numbers must appear in the 9 squares, but it can speed up the SAT-solver
		for j in range(9):
			x1, y1 = grouped_squares[j]
			for k in range(j + 1, 9):
				x2, y2 = grouped_squares[k]
				# this clause says that if number i is filled into square (x1, y1) then it cannot also be filled into (x2, y2)
				nand_clause = frozenset((-get_global_identifier(x1, y1, i), -get_global_identifier(x2, y2, i)))
				clauses.add(nand_clause)
	
	assert len(clauses) == 9 + 9 * 9 * 8 // 2 # another very basic sanity check
	
	return clauses
	
def generate_sudoku_base():
	"""
	Generates clauses that encode the basic conditions for the whole 9x9 Sudoku grid. This is equivalent to a Sudoku grid with 0 given numbers (i.e. not a valid Sudoku puzzle).
	
	There is some redundant information in the clauses created here, which is advantageous to the SAT-solver as it has more information to work with.
	Identical clauses (which do not provide extra information) are silently discarded due to the fact that a set is used.
	"""
	
	base_clauses = set()
	
	# generate the at-least-one clauses for the rows and columns
	for n in range(9):
		# generate the clauses for the nth column
		nth_column_clauses = generate_at_least_one([(n, i) for i in range(9)])
		base_clauses.update(nth_column_clauses) # in-place union of sets
		
		# generate the clauses for the n+1th row
		nth_row_clauses = generate_at_least_one([(i, n) for i in range(9)])
		base_clauses.update(nth_row_clauses) # in-place union of sets
	
	# generate the at-least-one clauses for the 3x3 subgrids
	for x_offset in range(0, 9, 3): # first subgrid starts at x=0, second at x=3, third at x=6
		for y_offset in range(0, 9, 3): # see above, also holds for y
			subgrid_clauses = generate_at_least_one([(x + x_offset, y + y_offset) for x in range(3) for y in range(3)])
			base_clauses.update(subgrid_clauses)
	
	# generate the at-most-one clauses for each square
	for x in range(9):
		for y in range(9):
			at_most_one_clauses = generate_at_most_one(x,y) # clauses encoding that at most one number may be in square (x,y)
			base_clauses.update(at_most_one_clauses)
	
	return base_clauses

def print_clauses(clauses: Iterable):
	"""
	Prints the given clauses in the DIMACS CNF format.
	
	DIMACS CNF format:
	Optionally at the beginning are comment lines which start with "c", e.g. "c This is a comment line".
	Then there is a line "p cnf <nv> <nc>", where <nv> is the number of variables and <nc> is the number of clauses in the CNF.
	Then the clauses follow, usually in separate lines, with the literals in the clauses being separated by whitespaces, and " 0" at the end to signify the end of the clause.
	E.g. the CNF given by {{-1, -2}, {1, -2}, {1, 2}} could be represented as the following DIMACS CNF output:
	p cnf 2 3
	-1 -2 0
	1 -2 0
	1 2 0
	"""
	print(f"p cnf {9 ** 3} {len(clauses)}")
	
	clause_list = list()
	
	# sort the literals in the clauses to get a more readable output
	for clause in clauses:
		# the key function applied here is not very nice but suitable due to the clause size limits
		clause_list.append(tuple(sorted(clause, key=lambda x:abs(x))))
	
	# sort the clauses themselves to get a more readable output
	# as above, computationally there is some redundancy here that could be improved but for just ~3200 clauses it does not matter
	clause_list.sort(key=lambda x: (len(x),) + tuple(abs(i) for i in x))
	
	for clause in clause_list:
		print(" ".join([str(lit) for lit in clause]) + " 0")


def array_to_clauses(puzzle: np.array):
	"""
	Converts a (partially) filled out Sudoku in array form into (unit) clauses.
	
	puzzle: a 9x9 array filled with the numbers from 0 to 9. Zeroes denote unfilled squares.
	"""
	
	assert puzzle.shape == (9, 9), f"input array has wrong shape in 'array_to_clauses' call, should be (9, 9) but is: {array.shape}"
	assert 0 <= np.min(puzzle) and np.max(puzzle) <= 9, f"input array entries out of bounds (>= 9 or <= 0) in 'array_to_clauses' call: {repr(array)}"
	
	# the unit clauses
	clauses = set()
	
	for x in range(9):
		for y in range(9):
			i = puzzle[y, x]
			if i > 0:
				clauses.add(frozenset((get_global_identifier(x, y, i),)))
	
	return clauses


def get_complete_sudoku_clauses(puzzle: np.array):
	"""
	Converts a 9x9 Sudoku with some givens into a CNF and returns that formula.
	
	puzzle: a 9x9 array filled with the numbers from 0 to 9. Zeroes denote unfilled squares.
	"""
	assert puzzle.shape == (9, 9), f"input array has wrong shape in 'array_to_clauses' call, should be (9, 9) but is: {array.shape}"
	assert 0 <= np.min(puzzle) and np.max(puzzle) <= 9, f"input array entries out of bounds (>= 9 or <= 0) in 'array_to_clauses' call: {repr(array)}"
	
	clauses = array_to_clauses(puzzle)
	clauses.update(generate_sudoku_base())
	
	return clauses


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
	
	from sudoku_examples import sdk_givens, sdk_filled
	
	#solve_and_compare(sdk_givens[0], sdk_filled[0])
	#solve_and_compare(sdk_givens[1], sdk_filled[1])
	solve_and_compare(sdk_givens[2], sdk_filled[2])
	
	#solve_and_compare(sdk_givens[0])
	
	
	#draw_sudoku(sdk_givens[0])
	
	#draw_attempt(sdk_givens[0], sdk_filled[0])
	
	#draw_attempt(sdk_givens[0], sdk_givens[0])
	


