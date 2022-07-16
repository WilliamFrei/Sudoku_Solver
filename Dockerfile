FROM python:3.8-slim
WORKDIR /build
COPY . /build
RUN pip3 install -r requirements.txt
COPY ./.env.docker.json /build/.env.json
EXPOSE 8085
CMD ["python3", "web_input.py"]

