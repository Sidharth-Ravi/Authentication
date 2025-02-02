# Authentication
## Instructions

- create virtual environment
`python -m venv venv`   

- activate your virtual environment 
`venv\Scripts\activate`

- install dependencies
`pip install -r requirements.txt`

- run migrations
`manage.py makemigrations Users`
`python manage.py migrate`
 
 - run server
 `python manage.py runserver`

 ## Testing
 - use the postman collection for testing `Authentication System.postman_collection.json`

 - run unit test 
 `python manage.py test`



