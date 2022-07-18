# "Dockerfile" needs to be build first with tag "sudoku-solver-base"
# docker build -f main.Dockerfile -t "sudoku-solver-main" .
FROM sudoku-solver-base:latest
COPY Main.py /build/
CMD ["python3", "Main.py"]

