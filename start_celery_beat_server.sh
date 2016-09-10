celery -A oinkbrew_webapp beat -b sqla+sqlite:///celerydb.sqlite -l info 
