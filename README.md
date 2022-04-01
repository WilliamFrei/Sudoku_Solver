# Sudoku-Solver

>**errare humanum est**

## What this program is for

When solving Sudokus, mistakes happen occasionally. Possible reasons are overlooking an already filled in number when checking for what is still missing, switching up rows or columns, or simply faulty solving logic, among other things.
When this happens, it is usually only after you fill out several more (potentially wrong, as a consequence of the original mistake) squares that you notice a the mistake has transpired.
At this point, it can be very hard to pinpoint the original mistake and backtrack. This program tries to help with that, by showing you all the squares that are filled in wrong.

To solve the Sudoku, a SAT-Solver which uses DPLL is employed. Typically, it only takes a fraction of a second to solve a valid Sudoku puzzle and check whether the solution found is unique.

## Example

![Sudoku-Puzzle](example_images/0_sudoku_given.png?raw=true)

You try to solve the Sudoku puzzle above.

![Sudoku-Attempt](example_images/1_sudoku_attempted.png?raw=true)

At some point your solving attempt reaches the stage of the second image. Here, you notice that in the lower left 3x3-subgrid, there must be a 3, a 6 and a 9 in the middle column, but also that neither of the three numbers can be in the center of the subgrid - thus there must be a mistake, and at least one of the 3s, 6s or 9s you filled in must be wrong.

Unfortunately, it is extremely difficult for a human to backtrack when the mistake happened, and how many of the other squares you filled in are wrong. Rather than doing that, it's probably simpler to just redo the puzzle from the beginning and hope you don't make another mistake.

However, what may be (almost) impossible for a human, can be trivial to a computer:
Provided with the 'givens' (the original puzzle) and the numbers you filled in, 
this program solves the Sudoku from the 'givens', and shows you which of the numbers you filled in correctly or incorrectly:

![Sudoku-Mistakes](example_images/2_sudoku_mistakes.png?raw=true)

Now you can just erase the wrong numbers and continue your solving attempt from there!
