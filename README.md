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
