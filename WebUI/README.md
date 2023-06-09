# Cohort-Analysis-Dashboard

A Tool for Cohort Based Process Analysis powered by [PM4PY](https://pm4py.fit.fraunhofer.de/)

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

3. You application is up and running. Navigate to `http://127.0.0.1:8000/` to start using CAD

### Linters and Fixes

1. CAD is using `flake` for detecting basic lint issues. You can find all lint constraints by running: `flake ./`

2. Most lint issues, such as incorrect indentations, can be fixed by `black` library. Just run `black ./`

3. The rest of the mising lint issues will have to be fixed manually

4. Additionally, it's possible to get a detailed overview and rating of each module

   Run `pylint ./{directory-name}`

NOTE: pylint and black are following pep8 styling standard.

### Running the Unit Tests

You can trigger the unit tests of an application by running `python manage.py test`
E.g. `python manage.py test log_management`

### Running CAD in a Docker container

1. Navigate to the root of the folder (Hint: where Dockerfile is located)

2. Create a CAD Docker image by running `docker build --tag cad .`

3. Start CAD in a container using `docker run --publish 8000:8000 cad`

4. You should be able to access CAD on `http://127.0.0.1:8000/`
