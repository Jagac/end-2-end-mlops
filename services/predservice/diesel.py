from tasks.factory import DieselTask

if __name__ == "__main__":
    diesel_celery = DieselTask().fuel_task()
    diesel_celery.worker_main(["-Q", "diesel_queue", "--loglevel=INFO"])
