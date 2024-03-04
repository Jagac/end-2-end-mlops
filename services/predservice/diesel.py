from tasks.factory import DieselTask


app = DieselTask().diesel_celery

if __name__ == "__main__":
    lpg_celery = DieselTask().fuel_task()
    worker = app.Worker(queues=["diesel_queue"], loglevel="INFO")
    worker.start()
