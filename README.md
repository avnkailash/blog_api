# MAV Blog Back-end
This project holds the back-end API of a basic blog.

## Description
This API can be used to perform the following operations:
- User creation, password updates
- Token based user login
- Blog post creation, updates, deletes and list the posts
- Comments can be added to a given blog post. The basic CRUD operations are supported.

### Test-Driven Development Philosophy
This back-end is developed based on TDD approach. All the features are implemented only after the test cases are created and tested that they are failing. The feature implementation simply targetted at making the test cases pass. This approach ensures that our code satisfies the feature requirements and we do not introduce any breaking changes.

## Prerequisites
- Docker
- Docker Compose
- Sufficient storage space to be able to build the containers and run them.
- This project tries to bind the port `8000` to make the API service available locally. Ensure to update that if the port is being used by some other service.

## Technology Stack
- Python3.6
- Django and DRF
- Docker for containerization
- sqlite for DB
- ModHeader plugin for Chrome. This plugin helps us to add / change header values for accessing authenticated end-points.

## Starting the Project
We can start this project in two ways.
1. Starting the server locally.
2. Spinning off a docker container.

#### 1. Start the server locally
The following steps will help you to start the project locally without relying on the docker service.
1. Setup a virtual environment. I used virtualenv for managing my virtual environment and the project dependencies in an isolated manner.
```commandline
virtualenv -p python3.6 .venv
```
2. Activate the virtual environment
```commandline
source .venv/bin/activate
```
3. After the virtual env is activated, we now need to install the project dependencies.
```
pip install -r requirements.txt
```
4. Now the project is ready with the required setup. Start the dango instance using the following command.
```commandline
python manage.py runserver
```
5. The service will be available on post `8000`. Navigating to http://localhost:8000/api/post/ should show you the blog post APIs.
6. We also have user creation, login API at http://localhost:8000/api/user/ API end-point

#### 2. Start the docker instance
You need to first build the image and then bring up the container. Here are the steps required to start the dockerized instance:
1. Build the docker image. Execute this command from blog_api directory in the terminal.
```commandline
docker-compose build
```
2. Start the container
```commandline
docker-compose up
```
3. The service will be available on post `8000`. Navigating to http://localhost:8000/api/post/ should show you the blog post APIs.
4. We also have user creation, login API at http://localhost:8000/api/user/ API end-point

## Testing the API
This project has been developed using TDD approach. It has 36 test cases included to guide me in the development of the features. Also, I have used flake8 to ensure python coding standards are followed. Use the following command to run the test cases and the flake8 checks.
```commandline
docker-compose run app sh -c "python manage.py test && flake8"
```
If you are running the code locally, then instead of the above docker command, you should use
```commandline
python manage.py test && flake8
```

### Important
If you wish to run the project locally, do not forget to create the required directories in the `/vol`
```commandline
/vol/web/media
/vol/web/media
```
these two directories are required to be able to upload images. And also, the current user needs to have proper read-write-execute permissions to the /vol and its sub-directories.