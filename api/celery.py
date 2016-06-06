from __future__ import absolute_import

from celery import Celery

app = Celery('api',
             broker='amqp://guest:guest@127.0.0.1:5672/',
             backend='amqp://guest:guest@127.0.0.1:5672/',
             include=['api.tasks.LogsMessage', 'api.tasks.RequestConfigurations',
                      'api.tasks.SensorCalibration', 'api.tasks.StatusMessage',
                      'api.tasks.InfluxCleanUp'])

app.conf.update(
    CELERY_TASK_RESULT_EXPIRES=3600,
)

if __name__ == '__main__':
    app.start()
