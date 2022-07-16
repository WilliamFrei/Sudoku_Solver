#!/usr/bin/env python

def test_global_identifier():
	"""
	Tests the functions that are imported below for producing valid outputs given valid inputs.
	
	Each global identifier in the range from 1 to 729 should be generated exactly once.
	Additionally it tests whether 'get_global_identifier' and 'split_global_identifier' behave as inverse functions given valid inputs.
	"""
	from modules.generate_sudoku_cnf import get_global_identifier, split_global_identifier
	
	# the sets holding the generated numbers
	identifier_map = {}
	
	# the ranges in the loops below are chosen according to the number of variables that occur in a CNF-encoding of a Sudoku 
	
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



if __name__ == '__main__':
	print("Running 'test_global_identifier'")
	test_global_identifier()
	print("Tests of 'test_global_identifier' successful")

