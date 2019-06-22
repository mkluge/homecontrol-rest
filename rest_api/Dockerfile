FROM ubuntu:latest
MAINTAINER Michael Kluge "vollseil@arcor.de"
RUN apt-get update -y
RUN apt-get install -y python3-pip python3-dev build-essential liblirc-dev
COPY . /app
WORKDIR /app
RUN pip3 install -r requirements.txt
ENTRYPOINT ["python3"]
CMD ["api_entry.py"]

