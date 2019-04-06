#This is the base image of the container
FROM python:2-slim

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

#Adding the basic python file to the Docker Script
ADD GetDataJSON.py /

#Install any needed packages specified in requirements.txt
RUN pip install --trusted-host pypi.python.org -r requirements.txt

#Added the port number on which the application will run
EXPOSE 5000

#Run the application
ENTRYPOINT ["python", "./GetDataJSON.py"]

