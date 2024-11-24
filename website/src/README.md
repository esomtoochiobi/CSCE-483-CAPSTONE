## CSCE 483 - WaCo Backend
1. Install pipenv 
   > pip install pipenv --user 
2. Install requirements
    > pipenv install
3. Run Flask app
    > pipenv run flask run
4. In three seperate terminals, run one command.
    > redis-server
    > pipenv run rq worker
    > pipenv run rqscheduler