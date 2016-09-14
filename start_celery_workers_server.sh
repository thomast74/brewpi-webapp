celery -A oinkbrew_webapp worker -b sqla+mysql://oinkuser:Amara@localhost/celery -P threads -l info
