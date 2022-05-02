# Sudoku-Solver

>**errare humanum est**

## What this program is for

When solving Sudokus, mistakes happen occasionally. Possible reasons are overlooking an already filled in number when checking for what is still missing, switching up rows or columns, or simply faulty solving logic, among other things.
When this happens, it is usually only after you fill out several more (potentially wrong, as a consequence of the original mistake) squares that you notice a the mistake has transpired.
At this point, it can be very hard to pinpoint the original mistake and backtrack. This program tries to help with that, by showing you all the squares that are filled in wrong.

To solve the Sudoku puzzle, it is converted into a CNF-formula and then a SAT-Solver which uses DPLL is employed. Typically, it only takes a fraction of a second to solve a valid Sudoku puzzle and check whether the solution found is unique.

## Contents

### Use-Case Example

[Example.md](Example.md) shows an example use-case without any code.

### Web-App

A dash-based web application can be found at [web_input.py](web_input.py). It can be used to enter a Sudoku puzzle alongside with the user's filled-in numbers, and will then show which of the numbers were filled in correctly/incorrectly. It requires installing the python packages found in `requirements.txt`.

### Jupyter-Notebook

[Code-Demo.ipynb](Code-Demo.ipynb) demonstrates some of the functions that are found in the modules, e.g. how Sudokus can be entered as numpy arrays, how they can be solved, and how the solutions can be visualised. As with the web application, running it also requires installing the python packages found in `requirements.txt`.

### Other Modules

The other `.py` files contain even more code, with lots of comments that explain what they do. `Main.py` contains mostly glue code tying together the other modules. The SAT-Solver is found in `Solver.py` (it contains some Sudoku-domain-specific knowledge such as the maximum number of variables, or code that ensures that there is only be a single solution, but could be made into a general-purpose SAT-Solver with only minor changes), and small helper functions used for the Solver are contained in `util.py`. `sudoku_examples.py` is made up of only some example puzzles and solving attempts. Lastly, as its name implies, `visualisation.py` is filled with a few functions to visualise Sudokus.

