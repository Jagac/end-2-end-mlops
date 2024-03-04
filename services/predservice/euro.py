from tasks.factory import Euro95Task


app = Euro95Task().euro_celery

if __name__ == "__main__":
    lpg_celery = Euro95Task().fuel_task()
    worker = app.Worker(queues=["euro_queue"], loglevel="INFO")
    worker.start()

