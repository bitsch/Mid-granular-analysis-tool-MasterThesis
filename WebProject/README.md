# Mid-granular-analysis-Tool

A Tool for Mid granular Analysis powered by [PM4PY](https://pm4py.fit.fraunhofer.de/)

## Developers

### Setting up local Virtual Environment

1. To create a new environment: `conda create --name [env-name] django`

2. To activate the environment specified above: `conda activate [env-name]`

3. To deactivate the environment : `conda deactivate`

**Note:** You can check the existing env by running `conda env list`

### Starting the application

1. Installing necessary project dependencies:

   `python3 -m pip install -r requirements.txt`

2. In order to start the application, you can use:

   `python manage.py runserver`

3. You application is up and running. Navigate to `http://127.0.0.1:8000/` to start using framework

### Running the framework in a Docker container

1. Navigate to the root of the folder (Hint: where Dockerfile is located)

2. Create a framework Docker image by running `docker build --tag framework .`

3. Start framework in a container using `docker run --publish 8000:8000 framework`

4. You should be able to access framework on `http://127.0.0.1:8000/`
