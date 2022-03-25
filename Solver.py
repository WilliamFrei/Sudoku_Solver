"""
A simple SAT-Solver, capable of solving Sudokus.

It determines whether a Sudoku has at least one solution.
Given a solution, it also determines whether a Sudoku has more solutions.
If there is only one solution, outputs the solution (if it exists) in a concise format.

Ideally the solver takes less than 0.1s to do find a solution and check it for uniqueness.
"""


import numpy as np

from collections.abc import Iterable

from util import magnitude_sign
from util import twos_complement
from util import magnitude as var
from util import is_positive as sign
from util import complement as compl


class Solver:
	
	def __init__(self, clauses: Iterable, n_vars: int, is_main_solver=True):
		"""
		Constructor for the solver
		
		clauses: a collection of clauses, each clause is a collection of variables which are either in the range [1, n_vars] or in the range [-n_vars, -1]
		n_vars: the number of variables appearing in the clauses
		is_main_solver: whether this is the main solver or a sub-solver created in a DPLL-split in a variable
		"""
		self.original_clauses = clauses # store the original clauses - we need them later to check for uniqueness of solutions
		self.n_vars = n_vars # store the n_vars
		self.clauses = [set() for _ in range(2 * n_vars)] # for each literal, a set of clauses where that literal occurs in (number of literals = 2x number of variables)
		# two unused extra lists are created so that we don't have to switch from 1-based indexing back to 0-based indexing every time
		self.units = [] # a list of literals found in unit clauses, we use a list as we are interested in the order
		self.var_states = np.zeros((n_vars, 2), dtype=bool) # states for variables that are assigned to a single polarity (i.e. units), used for checking for duplicates or contradictions
		# var_states[n, 0] = boolean encoding whether variable n has been assigned, var_states[n, 1] = boolean to which value variable n has been assigned (only relevant if the first value is True)
		
		# two-pass: first we convert all variables into magnitude-sign, then we construct our own data structures
		# first pass:
		temp_clauses = [map(magnitude_sign, clause) for clause in clauses]
		# second pass:
		for cl in temp_clauses:
			clause = frozenset(cl) # we want a frozenset, regardless of what it was before
			for literal in clause:
				self.clauses[literal].add(clause)
				if len(clause) == 1: # if it is an unit clause, add the literal to the units
					assert sign(literal) # if a negative literal unit clause would end up here, then a mistake when generating the Sudoku puzzle has happened - initial units must be > 0
					self.add_unit(literal)
		
		self.is_main_solver = is_main_solver
		self.is_solved = False # whether the formula has been solved
	
	def add_unit(self, literal):
		assert not self.var_states[var(literal), 0] # variable being assigned twice - this should not happen
		self.units.append(literal)
		self.var_states[var(literal), ] = (True, sign(literal))
	
	def solve(self, start_idx=0):
		# do unit propagation
		idx = start_idx
		while idx < len(self.units):
			literal = self.units[idx]
			
			# go over all clauses where that literal occurs in that polarity
			# remove them from the formula, as they are satisfied
			for rem_clause in self.clauses[literal]:
				# to remove the clause from the formula, remove it from all literals referencing it
				for member_literal in rem_clause:
					if member_literal == literal:
						continue
					assert rem_clause in self.clauses[member_literal], f"{member_literal},\n{rem_clause},\n{self.clauses[member_literal]}"
					self.clauses[member_literal].remove(rem_clause)
			
			self.clauses[literal] = frozenset()
			
			# go over all clauses where the literal occurs in the other polarity
			# remove the literal in the other polarity from those clauses, as the literal cannot be true in that polarity and thus cannot contribute to satisfying that clause
			# if this results in new unit clauses, add the units to the respective collections
			# if this results in the empty clause, the formula is unsatisfiable
			complement = compl(literal)
			for mod_clause in self.clauses[complement]:
				new_clause = set(mod_clause)
				assert complement in new_clause, f"{complement}, {new_clause}"
				new_clause.remove(complement)
				new_clause = frozenset(new_clause)
				
				if len(new_clause) == 1: # unit clause produced -> the variable of the remaining literal has to be assigned to that polarity
					unit_literal, = new_clause # extract the one element
					if self.var_states[var(unit_literal), 0]: # check whether it is already assigned
						# if it is assigned to the polarity we just learned about, then everything is fine
						# otherwise we derived a contradiction
						if self.var_states[var(unit_literal), 1] != sign(unit_literal):
							return False
					else: # if the variable is not assigned to anything yet, add the newly learned unit clause
						self.add_unit(unit_literal)
						
				elif len(new_clause) == 0: # empty clause produced
					return False # empty clause is a contradiction -> formula is unsolvable
				
				for member_literal in new_clause:
					assert mod_clause in self.clauses[member_literal], f"{self.clauses[member_literal]}"
					self.clauses[member_literal].remove(mod_clause) # remove the old clause which includes the literal
					self.clauses[member_literal].add(new_clause) # add the new clause with the literal removed
				
			# wipe the clauses of the complementary literal, permanently
			self.clauses[compl(literal)] = frozenset()
			
			idx += 1
		
		# if we found an assignment to all variables which didn't result in any contradictions (empty clauses, see above), we are done
		if len(self.units) == 9 ** 3:
			# if this is the main solver, we check if there are more solutions, otherwise we are done
			return self.check_uniqueness() if self.is_main_solver else True
		
		# otherwise, choose a variable that isn't assigned yet and try check whether the formula is satisfiable for either assignment of the variable
		literal = self.select_literal()
		for bit in [0, 1]: # the bit selects the polarity of the literal
			# create a Solver instance with the additional information about an extra unit clause of the literal
			sub_solver = Solver(frozenset(), 0, False) # dummy constructor call to get an instance
			# copy over the variables necessary for solving manually
			length = np.sum([len(cls) for cls in self.clauses])
			sub_solver.clauses = [cls.copy() for cls in self.clauses] # here we need to copy 1 layer deep because we have a collection of sets
			sub_solver.units = self.units.copy() # collection of primitives, shallow copy is fine
			sub_solver.var_states = self.var_states.copy() # collection of primitives
			# add the additional unit clause
			sub_solver.add_unit(literal ^ bit)
			# check if that instance satisfies the formula
			if sub_solver.solve(idx):
				# if it does, copy over the variable assignment and exit the function
				self.units = sub_solver.units
				self.var_states = sub_solver.var_states
				# if this is the main solver, we check if there are more solutions, otherwise we are done
				return self.check_uniqueness() if self.is_main_solver else True
		
		# DPLL lead to a negative result - the formula is unsolvable
		return False
	
	def select_literal(self):
		# select all variables that haven't been assigned yet
		unassigned_vars = list(np.flatnonzero(np.invert(self.var_states[:, 0])))
		assert len(unassigned_vars) > 0 # if there are no unassigned variables left, then this method should not have been called
		# apply a heuristic: sort the unassigned variables by number of positive occurrences and return one of those minimizing that metric
		unassigned_vars.sort(key=lambda v: -(len(self.clauses[v * 2]))) # since we convert from var to (positive) literal, we multiply by 2
		return unassigned_vars[0] * 2 # we know from the assert above that there has to be at least one
	
	def check_uniqueness(self):
		# make a copy of the original clauses (though we could also just use the collection directly)
		new_clauses = self.original_clauses.copy()
		# add a new clause that excludes the solution found
		# to do this we select all variables that were set to true
		# make a clause with the polarity of all corresponding literals reversed
		extra_clause = frozenset(twos_complement((var * 2) ^ 1) for var in np.flatnonzero(self.var_states[:, 1]))
		new_clauses.add(extra_clause)
		sub_solver = Solver(new_clauses, self.n_vars, False)
		original_solution_is_unique = not sub_solver.solve() # if true, then there are additional solutions, which should not be the case.
		self.is_solved = original_solution_is_unique
		return original_solution_is_unique
	
	def get_solution(self):
		#assert self.is_solved 
		assert len(self.units) == 9 ** 3 # number of unit clauses = number of variables if all went well
		assert all(self.var_states[:, 0]) # redundant with the assert above unless there are bugs - which you can never be sure of so double checking is better
		return np.flatnonzero(self.var_states[:, 1]) + 1 # return all variables that are set to true, incremented by 1 as we expect them to be 1-based outside of this class
	
	
