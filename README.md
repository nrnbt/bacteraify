# Django Project README

This is a Django project that uses a virtual environment (venv) for managing dependencies. Follow the instructions below to set up the project on your local machine.

## Prerequisites

Before you get started, make sure you have the following installed:

- Python 3.10.8
- `virtualenv` (if not already installed)

## Getting Started

1. Clone the repository to your local machine:

   git clone git@github.com:nrnbt/bacteraify.git
   cd bacteraify
   pip install -r requirements.txt

## Use Virtual Env
1. use "pip install virtualenv" for install virtual env of python
2. run "python -m venv venv"
3. go to root directory of project and type Scripts\activate.bat

## Start project
Use "python manage.py runserver" command for start project

## To enable consumer
1. Start redis server
2. Use "daphne bacteraify.asgi:application --port 8001" command to start asgi on port 8001