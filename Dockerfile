
# The original Dockerfile is missing the EXPOSE instruction to expose the TCP port.
# We need to add EXPOSE before the CMD instruction to expose the port.

FROM python:3.8.2

WORKDIR /e-voting-with-django

COPY . /e-voting-with-django/

# Add additional debugging commands to check the contents of the directory and the requirements.txt file
RUN ls -al
RUN cat requirements.txt

# Install the required packages from requirements.txt
RUN pip install -r requirements.txt

# Expose the TCP port 8080
EXPOSE $PORT

# Modify the CMD instruction to run the application using 127.0.0.1 instead of 0.0.0.0
CMD ["python", "manage.py", "runserver", "0.0.0.0:$PORT"]
