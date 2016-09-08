celery -A oinkbrew_webapp worker -b sqla+sqlite:///celerydb.sqlite -P threads -l info --detach
