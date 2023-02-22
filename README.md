# Advanced_Recipe_API

### Features :

- 19 Endpoints
- User Authentication
- Browsable Admin Interface
- Browsable API (Swagger)

### Technologies :

- Python
- Django
- Django Rest FrameWork
- PostGreSQL
- Docker (Dockerizes Service of API) and (Dockerized Service of DataBase)
- Swagger (Automated Documentation for API)
- GitHub Actions (Testing and Linting)

### Project structure :
- app/ - django project
- app/core - code shared between multiple apps
- app/user - user related code
- app/recipe - recipe related code

### Development Approach

- Test Driven Development
- Write test -> Run Test (fails) -> Add feature -> Run Test (Passes) -> Re-factor -> Run Test

# Project setup

- Create a new project
- Using Docker w/ Django
- Setup new Django Project
- Linting and Testing
- Using docker compose

### Docker steps :
- Define Dockerfile (Contains all the operating system dependencies that our project needs )
- Create Docker Compose Configuration (How to run the images that are created from our Docker file configuration)
- Run All commands via docker compose
