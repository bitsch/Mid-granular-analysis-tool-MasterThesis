FROM python:3.8

# Create a working directory on virtual env
WORKDIR /app

# Copy and install the requirements
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

# Copy all the files from current directory to the virtual env
COPY . .

RUN python3 manage.py migrate

# Start server
CMD [ "python3", "manage.py", "runserver", "0.0.0.0:8000" ]