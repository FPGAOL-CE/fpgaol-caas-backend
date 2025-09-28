FROM python:3.10

WORKDIR /app

RUN apt-get update && apt-get install -y docker.io podman
RUN pip install tornado aiofiles requests

EXPOSE 18888

ENV CHIPDB_PATH /chipdb
ENV JOB_PATH /jobs
RUN mkdir -p $CHIPDB_PATH
RUN mkdir -p $JOB_PATH

COPY . .

# Command to start the Tornado server
CMD ["python", "server.py"]
