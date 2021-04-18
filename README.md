## Flask project (developed on Windows OS)

Create a virtual enviroment via `python3 -m venv <name_of_virtualenv>`

Activate your virtual enviroment `venv\scripts\activate`

Run `pip install -r requirements.txt`

Run `set FLASK_APP=setup.py`

Run `set FLASK_DEBUG=1`

Run `flask db init`

Run `flask db migrate -m "Initial migration"`

Run `flask db upgrade`

Now `flask run`

## You will need an application to test mail activation account

Download [MailHog](https://github.com/mailhog/MailHog/blob/master/docs/RELEASES.md) for your Machine 

Run mailhog so you can see the emails for your account confirmation

### Extra configuration

Before do this, stop the flask app. You will need to download [redis](https://redis.io/) and set the port to 6370 ( and check if the service is up). 

Open another window in the same project directory, active the virtual enviroment too. Then run `celery -A setup.celery worker --loglevel=info -P eventlet`

Then go to `app\__init__.py` on line 22  set the `SEND_MAILS_WITH_CELERY` property to `True` .

You should have three windows open:

- One running MailHog 

- One running the Celery task (under your virtual enviroment)

- And another one running the flask app (also under virtual enviroment)  
  
  

With this configuration in place, everything should work...
