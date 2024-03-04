from tasks.factory import LpgTask


app = LpgTask().lpg_celery

if __name__ == "__main__":
    lpg_celery = LpgTask().fuel_task()
    worker = app.Worker(queues=["lpg_queue"], loglevel="INFO")
    worker.start()

