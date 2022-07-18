# the base docker image from which the others are derived
# the image that is created should be tagged "sudoku-solver-base" to be accessible for the other Dockerfiles:
# e.g. build with: docker build -t "sudoku-solver-base" .
FROM python:3.8-slim
WORKDIR /build
COPY . /build
RUN pip3 install -r requirements.txt

