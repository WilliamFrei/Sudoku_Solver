# Sudoku-Solver

>**errare humanum est**

## What this program is for

When solving Sudokus, mistakes happen occasionally. Possible reasons are overlooking an already filled in number when checking for what is still missing, switching up rows or columns, or simply faulty solving logic, among other things.
When this happens, it is usually only after you fill out several more (potentially wrong, as a consequence of the original mistake) squares that you notice a the mistake has transpired.
At this point, it can be very hard to pinpoint the original mistake and backtrack. This program tries to help with that, by showing you all the squares that are filled in wrong.

To solve the Sudoku puzzle, it is converted into a CNF-formula and then a SAT-Solver, which uses DPLL, is employed. Typically, it only takes a fraction of a second to solve a valid Sudoku puzzle and check whether the solution found is unique.

## Contents

### Use-Case Example

[Example.md](Example.md) shows an example use-case without any code.

### Installation

To run the code in this repository, it is necessary to have python3 installed. Then the following steps should be executed:

* Create a virtual python environment:

``python3 -m venv venv``

* Activate the virtual environment:

``. venv/bin/activate``

* Install the required python modules listed in `requirements.txt` in the virtual enronment:

``pip install -r requirements.txt``

* Run either the main file or the web app:

``python main.py``

``python web_input.py``

* For more information on either, see below

### Web-App

A dash-based web application can be found at [web_input.py](web_input.py). It can be used to enter a Sudoku puzzle alongside with the user's filled-in numbers, and will then show which of the numbers were filled in correctly/incorrectly. It can be run by building the Dockerfile and running the image, then accessing 0.0.0.0:8085 via a web brower (don't forget to forward the port by adding `-p 8085:8085` when running the image).

### Jupyter-Notebook

[Code-Demo.ipynb](Code-Demo.ipynb) demonstrates some of the functions that are found in the modules, e.g. how Sudokus can be entered as numpy arrays, how they can be solved, and how the solutions can be visualised. Running it requires installing the python packages found in `requirements.txt`.

### Other Modules

The other `.py` files in the `modules` folder contain even more code, with explanatory comments. `main.py` contains glue code tying together the other modules. The SAT-Solver is found in `solver.py`  - it uses some Sudoku-domain-specific knowledge such as the maximum number of variables, and code ensuring there is exactly one solution, but could be made into a general-purpose SAT-Solver with minor changes. The solver uses some  small helper functions which are found in `util.py`. `sudoku_examples.py` is made up of some example puzzles and solving attempts. Lastly, as its name implies, `visualisation.py` is filled with a few functions to visualise Sudokus.

