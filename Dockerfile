#Download base image Pyhon
FROM python:3.7
# LABEL about the custom image
LABEL maintainer="dl629@cornell.edu"
LABEL version="1.0"
LABEL description="The GUI for Quarz Fork Feedthrough calculations."
# Update Ubuntu Software repository

COPY . /app
WORKDIR /app/
# RUN apt-get install python3-tk
RUN pip install --upgrade pip
RUN pip install -r env/requirements.txt

CMD python3 /app/src/main_app.py
