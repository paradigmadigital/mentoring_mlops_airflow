FROM python:3.8

# Install al the required dependencies
COPY ./requirements.txt /home
WORKDIR /home
RUN  pip install -r requirements.txt

# Copy the folder path into the container
RUN mkdir /home/input
RUN mkdir /home/output
COPY ./ /home
