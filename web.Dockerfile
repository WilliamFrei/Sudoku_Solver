# "Dockerfile" needs to be build first with tag "sudoku-solver-base"
# example build command for this:
# docker build -f web.Dockerfile -t "sudoku-solver-web" .
# port 8050 needs to be forwarded when running the container
FROM sudoku-solver-base:latest
COPY .env.docker.json /build/.env.json
CMD ["python3", "web_input.py"]

