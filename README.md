# Django Project README

This is a Django project that uses a virtual environment (venv) for managing dependencies. Follow the instructions below to set up the project on your local machine.

## Prerequisites

Before you get started, make sure you have the following installed:

- Python 3.10.8
- `virtualenv` (if not already installed)
- python -m venv venv

## Getting Started

1. Clone the repository to your local machine:

   git clone git@github.com:nrnbt/bacteraify.git
   cd bacteraify
   pip install -r requirements.txt
   
2. Start MySQL server

   configure mysql env

## Use Virtual Env
1. use "pip install virtualenv" for install virtual env of python
2. run "python -m venv venv"
3. go to root directory of project and type Scripts\activate.bat

## To enable consumer
1. Start redis server
2. Use "daphne main.asgi:application --port 8001" command to start asgi on port 8001

## Start project
Use "python manage.py runserver" command for start project

## Static files
   run "python manage.py collectstatic --noinput"
   if USE_S3 is true on env it will use aws s3 bucket
   else static files will load from local

## To use scheduled task
   After running `redis` on machine run migrate:
      - python manage.py migrate django_celery_results
      - python manage.py migrate django_celery_beat

   run 
      - `celery -A main worker --loglevel=info` / in windows run : `celery -A main worker --pool=solo --loglevel=info` /
      - `celery -A main beat --loglevel=info`.

   to clear tasks run `celery -A main purge`