#!/usr/bin/env python

import numpy as np

# example original Sudoku puzzles without any numbers filled in by the user (zeroes are empty squares)
sdk_givens = [
       np.array([
       [0, 0, 0, 0, 6, 0, 0, 0, 0],
       [0, 0, 0, 7, 8, 1, 4, 0, 2],
       [0, 0, 8, 5, 9, 0, 3, 0, 6],
       [9, 3, 0, 0, 0, 0, 0, 2, 0],
       [0, 0, 6, 0, 5, 0, 0, 0, 0],
       [7, 8, 0, 0, 0, 2, 0, 9, 0],
       [0, 0, 2, 6, 7, 0, 5, 0, 1],
       [0, 0, 0, 3, 1, 5, 2, 0, 9],
       [0, 0, 0, 0, 0, 0, 0, 0, 0]], dtype=int),
       np.array([
       [7, 1, 0, 0, 3, 0, 0, 0, 0],
       [0, 0, 0, 0, 0, 0, 8, 0, 1],
       [0, 0, 0, 9, 4, 0, 6, 0, 0],
       [5, 0, 7, 6, 0, 0, 2, 0, 0],
       [0, 0, 0, 0, 8, 0, 0, 0, 0],
       [4, 0, 6, 3, 0, 0, 9, 0, 0],
       [0, 0, 0, 4, 2, 0, 7, 0, 0],
       [0, 0, 0, 0, 0, 0, 4, 0, 8],
       [3, 6, 0, 0, 9, 0, 0, 0, 0]], dtype=int),
       np.array([
       [4, 0, 8, 0, 0, 5, 7, 0, 0],
       [0, 0, 0, 0, 4, 0, 0, 5, 0],
       [1, 0, 0, 0, 8, 0, 0, 0, 4],
       [0, 9, 0, 6, 5, 0, 0, 0, 7],
       [0, 0, 3, 0, 0, 7, 6, 8, 0],
       [0, 0, 0, 0, 0, 4, 0, 0, 0],
       [0, 0, 0, 0, 9, 0, 0, 0, 5],
       [0, 0, 0, 0, 0, 1, 0, 0, 0],
       [7, 0, 0, 0, 0, 0, 3, 0, 2]], dtype=int)
       ]


# example Sudokus with numbers filled in by the user, some of them wrong (derived from the puzzles above)
sdk_filled = [
       np.array([
       [0, 0, 0, 2, 6, 3, 9, 0, 0],
       [0, 0, 0, 7, 8, 1, 4, 5, 2],
       [0, 0, 8, 5, 9, 4, 3, 0, 6],
       [9, 3, 1, 8, 0, 6, 7, 2, 5],
       [0, 0, 6, 9, 5, 7, 1, 0, 0],
       [7, 8, 5, 1, 3, 2, 6, 9, 4],
       [0, 9, 2, 6, 7, 8, 5, 0, 1],
       [8, 6, 0, 3, 1, 5, 2, 0, 9],
       [0, 0, 0, 4, 2, 9, 8, 6, 0]], dtype=int),
       np.array([
       [7, 1, 0, 8, 3, 6, 5, 4, 0],
       [6, 4, 0, 0, 2, 0, 8, 0, 1],
       [0, 0, 0, 9, 4, 1, 6, 7, 0],
       [5, 3, 7, 6, 1, 9, 2, 8, 4],
       [0, 0, 0, 7, 8, 4, 3, 0, 0],
       [4, 8, 6, 3, 5, 2, 9, 1, 7],
       [0, 0, 0, 4, 2, 8, 7, 0, 0],
       [0, 7, 0, 1, 6, 3, 4, 0, 8],
       [3, 6, 4, 5, 9, 7, 1, 2, 0]], dtype=int),
       np.array([
       [4, 6, 8, 2, 1, 5, 7, 9, 3],
       [9, 2, 7, 3, 4, 6, 1, 5, 8],
       [1, 3, 5, 7, 8, 9, 2, 6, 4],
       [2, 9, 1, 6, 5, 8, 4, 3, 7],
       [5, 4, 3, 9, 2, 7, 6, 8, 1],
       [8, 7, 6, 1, 3, 4, 5, 2, 9],
       [6, 1, 4, 8, 9, 2, 8, 7, 5],
       [3, 8, 2, 5, 7, 1, 9, 4, 6],
       [7, 5, 9, 4, 6, 0, 3, 1, 2]], dtype=int)
       ]



